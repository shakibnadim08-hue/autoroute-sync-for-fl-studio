# name=Auto-Route & Sync
# url=https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm

"""FL Studio Auto-Route & Sync.

This MIDI Controller Scripting entrypoint watches Channel Rack state and
organizes newly created channels without changing audio processing.
"""

import channels
import mixer
import midi
import patterns
import ui
import utils


MASTER_TRACK = 0
MAX_FX_SLOTS = 10
DELETE_CONFIRMATION_SCANS = 2
VERBOSE = False

# High-saturation, medium-brightness colors chosen to remain distinct in FL's
# dark UI. They are assigned in order first; a hue-based fallback continues
# generating vivid colors after this starter palette is exhausted. The same
# integer is applied to the Channel Rack and Mixer.
VIBRANT_COLORS = (
    utils.RGBToColor(255, 128, 48),
    utils.RGBToColor(255, 196, 48),
    utils.RGBToColor(176, 224, 48),
    utils.RGBToColor(64, 208, 96),
    utils.RGBToColor(48, 208, 160),
    utils.RGBToColor(48, 192, 224),
    utils.RGBToColor(64, 128, 255),
    utils.RGBToColor(112, 96, 255),
    utils.RGBToColor(176, 80, 240),
    utils.RGBToColor(224, 64, 208),
    utils.RGBToColor(224, 144, 64),
    utils.RGBToColor(208, 208, 64),
    utils.RGBToColor(128, 224, 64),
    utils.RGBToColor(64, 224, 128),
    utils.RGBToColor(64, 224, 208),
    utils.RGBToColor(64, 176, 240),
    utils.RGBToColor(96, 128, 240),
    utils.RGBToColor(160, 96, 240),
)


# The script acts only on channels that appear after this baseline. The map is
# intentionally session-local so a reload never guesses which old mixer
# tracks were created by this script.
_known_channel_ids = set()
_managed_tracks_by_channel_id = {}
_managed_tracks = {}
_orphaned_managed_tracks = {}
_managed_pattern_colors = {}
_pattern_color_baseline = {}
_next_color_index = 0
_last_channel_count = 0
_last_active_pattern = None
_pending_channel_scan = False
_pending_pattern_scan = False
_loading_project = False
_initialized = False


def _log(message):
    if VERBOSE:
        print("[Auto-Route & Sync] " + str(message))


def _safe_channel_id(channel_index):
    """Return a stable channel identity when the API provides one."""
    try:
        event_id = channels.getRecEventId(channel_index, True)
        if event_id is not None:
            return ("rec", int(event_id))
    except Exception:
        pass

    try:
        return (
            "fallback",
            int(channel_index),
            str(channels.getChannelName(channel_index, True)),
            int(channels.getChannelType(channel_index, True)),
        )
    except Exception:
        return ("fallback", int(channel_index))


def _current_channel_ids():
    ids = set()
    try:
        count = int(channels.channelCount(1))
    except Exception:
        return ids

    for channel_index in range(count):
        ids.add(_safe_channel_id(channel_index))
    return ids


def _capture_baseline():
    global _known_channel_ids, _managed_tracks_by_channel_id
    global _managed_tracks, _orphaned_managed_tracks
    global _managed_pattern_colors, _pattern_color_baseline
    global _last_channel_count, _next_color_index, _last_active_pattern

    _known_channel_ids = _current_channel_ids()
    _managed_tracks_by_channel_id = {}
    _managed_tracks = {}
    _orphaned_managed_tracks = {}
    _managed_pattern_colors = {}
    _pattern_color_baseline = {}
    try:
        pattern_total = int(patterns.patternMax())
        for pattern_index in range(1, pattern_total + 1):
            if not patterns.isPatternDefault(pattern_index):
                _pattern_color_baseline[pattern_index] = int(patterns.getPatternColor(pattern_index))
    except Exception:
        pass
    _last_channel_count = len(_known_channel_ids)
    _next_color_index = 0
    try:
        _last_active_pattern = int(patterns.patternNumber())
    except Exception:
        _last_active_pattern = None
    _log("Baseline captured: %d channel(s)" % len(_known_channel_ids))


def _mixer_insert_indices():
    """Return ordinary insert indices, excluding Master and Current."""
    try:
        total_tracks = int(mixer.trackCount())
    except Exception:
        return []

    if total_tracks <= 2:
        return []
    return list(range(1, total_tracks - 1))


def _occupied_by_channels():
    occupied = set()
    try:
        count = int(channels.channelCount(1))
    except Exception:
        return occupied

    for channel_index in range(count):
        try:
            target = int(channels.getTargetFxTrack(channel_index, True))
            if target > MASTER_TRACK:
                occupied.add(target)
        except Exception:
            pass
    return occupied


def _has_plugin(track_index):
    for slot in range(MAX_FX_SLOTS):
        try:
            if mixer.isTrackPluginValid(track_index, slot):
                return True
        except Exception:
            pass
    return False


def _has_inter_insert_route(track_index, insert_indices):
    """Avoid tracks with existing manual sends or incoming inter-insert audio."""
    for other_index in insert_indices:
        if other_index == track_index:
            continue
        try:
            if mixer.getRouteSendActive(other_index, track_index):
                return True
            if mixer.getRouteSendActive(track_index, other_index):
                return True
        except Exception:
            pass
    return False


def _find_free_mixer_track(occupied):
    insert_indices = _mixer_insert_indices()
    for track_index in insert_indices:
        if track_index in occupied:
            continue
        if _has_plugin(track_index):
            continue
        if _has_inter_insert_route(track_index, insert_indices):
            continue
        return track_index
    return None


def _used_channel_colors():
    colors = set()
    try:
        count = int(channels.channelCount(1))
    except Exception:
        return colors

    for channel_index in range(count):
        try:
            colors.add(int(channels.getChannelColor(channel_index, True)))
        except Exception:
            pass
    return colors


def _is_red(color):
    """Return True for colors that would be confused with FL selection red."""
    try:
        red, green, blue = utils.ColorToRGB(int(color))
        return red >= 220 and green <= 80 and blue <= 80 and red > green * 2.0 and red > blue * 2.0
    except Exception:
        return False


def _hsv_to_color(hue, saturation=0.82, value=1.0):
    """Convert HSV values to FL Studio's integer RGB color format."""
    hue = float(hue) % 360.0
    chroma = value * saturation
    sector = hue / 60.0
    x = chroma * (1.0 - abs((sector % 2.0) - 1.0))

    if sector < 1.0:
        red, green, blue = chroma, x, 0.0
    elif sector < 2.0:
        red, green, blue = x, chroma, 0.0
    elif sector < 3.0:
        red, green, blue = 0.0, chroma, x
    elif sector < 4.0:
        red, green, blue = 0.0, x, chroma
    elif sector < 5.0:
        red, green, blue = x, 0.0, chroma
    else:
        red, green, blue = chroma, 0.0, x

    match = value - chroma
    return int(utils.RGBToColor(
        int(round((red + match) * 255.0)),
        int(round((green + match) * 255.0)),
        int(round((blue + match) * 255.0)),
    ))


def _choose_vibrant_color():
    """Choose a vivid color not currently used by another channel."""
    global _next_color_index

    used = _used_channel_colors()
    palette_size = len(VIBRANT_COLORS)
    start = _next_color_index

    for offset in range(palette_size):
        index = start + offset
        color = int(VIBRANT_COLORS[index % palette_size])
        if color not in used and not _is_red(color):
            _next_color_index = index + 1
            return color

    # Continue through a large hue sequence instead of repeating the starter
    # palette. The golden-angle step distributes adjacent assignments around
    # the color wheel and makes collisions very unlikely.
    golden_angle = 137.507764
    for offset in range(720):
        color = _hsv_to_color((start + offset) * golden_angle)
        if color not in used and not _is_red(color):
            _next_color_index = start + offset + 1
            return color

    # A final deterministic fallback is practically unreachable, but keeps
    # the function total if a project already uses an unusually large color
    # set.
    color = _hsv_to_color(start * golden_angle, 0.70, 0.95)
    if _is_red(color):
        color = utils.RGBToColor(255, 196, 48)
    _next_color_index = start + 1
    return color


def _pattern_source_color():
    """Choose a contained-channel proxy color for the active pattern.

    FL Studio's MIDI API exposes the active pattern and its color, but does not
    expose a public pattern-to-channel membership query. The selected channel
    is therefore the strongest available signal; the first non-default channel
    is used as a fallback for mixed patterns.
    """
    try:
        selected = int(channels.selectedChannel(1, 0, 1))
    except Exception:
        selected = -1

    candidates = []
    if selected >= 0:
        candidates.append(selected)

    try:
        count = int(channels.channelCount(1))
    except Exception:
        count = 0
    for channel_index in range(count):
        if channel_index not in candidates:
            candidates.append(channel_index)

    for channel_index in candidates:
        try:
            color = int(channels.getChannelColor(channel_index, True))
            if color and not _is_red(color):
                return color
        except Exception:
            pass

    return _choose_vibrant_color()


def _sync_active_pattern_color():
    """Give a new/default active pattern a non-red channel-derived color."""
    global _last_active_pattern, _managed_pattern_colors

    try:
        pattern_index = int(patterns.patternNumber())
        current_color = int(patterns.getPatternColor(pattern_index))
    except Exception:
        return

    _last_active_pattern = pattern_index
    baseline_color = _pattern_color_baseline.get(pattern_index, None)

    # Do not overwrite an existing user-selected non-red pattern color. A
    # pattern that is new since the baseline, or still at its baseline color,
    # is eligible for automatic synchronization.
    eligible = pattern_index not in _pattern_color_baseline
    if baseline_color is not None and current_color == baseline_color:
        eligible = True
    if not eligible and not _is_red(current_color):
        return

    color = _pattern_source_color()
    if _is_red(color):
        color = _choose_vibrant_color()

    try:
        patterns.setPatternColor(pattern_index, color)
        _managed_pattern_colors[pattern_index] = color
        _log("Colored pattern %d" % pattern_index)
    except Exception as error:
        _log("Could not color pattern %d: %s" % (pattern_index, error))


def _track_is_targeted(track_index):
    try:
        count = int(channels.channelCount(1))
    except Exception:
        return False

    for channel_index in range(count):
        try:
            if int(channels.getTargetFxTrack(channel_index, True)) == track_index:
                return True
        except Exception:
            pass
    return False


def _clear_managed_track_plugins(track_index):
    """Remove effects from a managed insert after its source channel is gone.

    FL Studio's public scripting API exposes slot inspection and editor focus,
    but does not expose a direct delete-slot function. The safe supported
    sequence is therefore: focus the exact slot, verify that FL Studio reports
    the same active effect, press FL Studio's own Delete command, and verify
    that the slot is empty. If any verification step fails, leave the slot
    untouched rather than risking deletion from the wrong mixer location.
    """
    focus_editor = getattr(mixer, "focusEditor", None)
    active_effect = getattr(mixer, "getActiveEffectIndex", None)
    delete_key = getattr(ui, "delete", None)
    if focus_editor is None or active_effect is None or delete_key is None:
        _log("Cannot clear mixer insert %d: this FL Studio build has no verified slot-delete path" % track_index)
        return False

    get_focused_form_id = getattr(ui, "getFocusedFormID", None)
    set_focused = getattr(ui, "setFocused", None)
    set_track_number = getattr(mixer, "setTrackNumber", None)
    set_active_track = getattr(mixer, "setActiveTrack", None)
    mixer_window_id = getattr(ui, "widMixer", 0)

    cleared_any = False
    for slot in range(MAX_FX_SLOTS - 1, -1, -1):
        try:
            if not mixer.isTrackPluginValid(track_index, slot):
                continue

            # setTrackNumber is available on older FL Studio versions; keep
            # setActiveTrack as a newer-version fallback.
            if set_track_number is not None:
                set_track_number(track_index)
            elif set_active_track is not None:
                set_active_track(track_index)

            focus_editor(track_index, slot)
            expected_plugin_id = None
            try:
                expected_plugin_id = int(mixer.getTrackPluginId(track_index, slot))
            except Exception:
                pass

            focused_ok = False
            if get_focused_form_id is not None and expected_plugin_id is not None:
                try:
                    focused_ok = int(get_focused_form_id()) == expected_plugin_id
                except Exception:
                    pass
            if not focused_ok:
                try:
                    focused = active_effect()
                    focused_ok = focused is not None and tuple(focused) == (track_index, slot)
                except Exception:
                    focused_ok = False
            if not focused_ok:
                _log("Did not clear mixer insert %d slot %d: exact slot verification failed" % (track_index, slot))
                continue

            # Leave the exact effect selected, but move keyboard focus back to
            # the mixer window so ui.delete() acts on the mixer slot rather
            # than inside the plugin editor.
            if set_focused is not None:
                try:
                    set_focused(mixer_window_id)
                except Exception:
                    pass
            delete_key()

            if mixer.isTrackPluginValid(track_index, slot):
                # Some builds process the first Delete after focus transfer;
                # repeat only after re-selecting and re-verifying the same slot.
                if set_track_number is not None:
                    set_track_number(track_index)
                elif set_active_track is not None:
                    set_active_track(track_index)
                focus_editor(track_index, slot)
                retry_ok = False
                if get_focused_form_id is not None and expected_plugin_id is not None:
                    try:
                        retry_ok = int(get_focused_form_id()) == expected_plugin_id
                    except Exception:
                        pass
                if retry_ok:
                    if set_focused is not None:
                        try:
                            set_focused(mixer_window_id)
                        except Exception:
                            pass
                    delete_key()

            if not mixer.isTrackPluginValid(track_index, slot):
                cleared_any = True
                _log("Cleared mixer insert %d slot %d" % (track_index, slot))
            else:
                _log("Mixer insert %d slot %d remains occupied after verified Delete" % (track_index, slot))
        except Exception as error:
            _log("Could not clear mixer insert %d slot %d: %s" % (track_index, slot, error))
    return cleared_any


def _reset_managed_track(track_index, original_name, original_color):
    """Restore the insert appearance that existed before automation claimed it."""
    try:
        mixer.setTrackName(track_index, original_name)
        mixer.setTrackColor(track_index, original_color)
        _log("Restored mixer insert %d" % track_index)
    except Exception as error:
        _log("Could not restore mixer insert %d: %s" % (track_index, error))


def _cleanup_orphaned_managed_tracks():
    """Restore managed inserts after deletion is confirmed across idle scans.

    Mixer-track ownership is used instead of channel indices or REC event IDs.
    Channel indices and REC offsets can change when another channel is deleted;
    the mixer insert that automation claimed remains the reliable identity.
    """
    for track_index, original in list(_managed_tracks.items()):
        if _track_is_targeted(track_index):
            _orphaned_managed_tracks.pop(track_index, None)
            continue

        scans = _orphaned_managed_tracks.get(track_index, 0) + 1
        _orphaned_managed_tracks[track_index] = scans
        if scans < DELETE_CONFIRMATION_SCANS:
            continue

        original_name, original_color = original
        _clear_managed_track_plugins(track_index)
        _reset_managed_track(track_index, original_name, original_color)
        _managed_tracks.pop(track_index, None)
        _orphaned_managed_tracks.pop(track_index, None)


def _sync_new_channel(channel_index, occupied):
    """Color and route one newly created Channel Rack channel."""
    channel_id = _safe_channel_id(channel_index)

    try:
        current_target = int(channels.getTargetFxTrack(channel_index, True))
        name = str(channels.getChannelName(channel_index, True))
    except Exception as error:
        _log("Could not read channel %d: %s" % (channel_index, error))
        return

    if current_target > MASTER_TRACK:
        # Respect a route already created by FL Studio or the user.
        occupied.add(current_target)
        return

    color = _choose_vibrant_color()

    try:
        channels.setChannelColor(channel_index, color, True)
    except Exception as error:
        _log("Could not set Channel Rack color for channel %d: %s" % (channel_index, error))

    track_index = _find_free_mixer_track(occupied)
    if track_index is None:
        _log("No unused mixer insert is available for channel %d" % channel_index)
        return

    try:
        # Preserve the track’s original appearance so deletion can restore it
        # exactly, including FL Studio’s theme-specific default color.
        original_name = str(mixer.getTrackName(track_index))
        original_color = int(mixer.getTrackColor(track_index))
    except Exception:
        original_name = ""
        original_color = 0

    try:
        # Some FL Studio builds report default Master as 0, others as -1.
        channels.setTargetFxTrack(channel_index, track_index, True)
        mixer.setTrackName(track_index, name)
        mixer.setTrackColor(track_index, color)
        mixer.afterRoutingChanged()
        occupied.add(track_index)
        _managed_tracks_by_channel_id[channel_id] = (
            track_index,
            original_name,
            original_color,
        )
        _managed_tracks[track_index] = (original_name, original_color)
        _orphaned_managed_tracks.pop(track_index, None)
        _log("Routed '%s' to mixer insert %d" % (name, track_index))
    except Exception as error:
        _log("Could not sync channel %d: %s" % (channel_index, error))


def _scan_for_channel_changes():
    """Detect additions, deletions, and replacements in the Channel Rack."""
    global _known_channel_ids, _last_channel_count

    if _loading_project or not _initialized:
        return

    try:
        count = int(channels.channelCount(1))
    except Exception:
        return

    previous_ids = set(_known_channel_ids)
    current_ids = []
    new_indices = []
    for channel_index in range(count):
        channel_id = _safe_channel_id(channel_index)
        current_ids.append(channel_id)
        if channel_id not in previous_ids:
            new_indices.append(channel_index)

    current_id_set = set(current_ids)
    _cleanup_orphaned_managed_tracks()

    # Update before routing so our own refresh cannot duplicate work.
    _known_channel_ids = current_id_set
    _last_channel_count = len(current_ids)

    if not new_indices:
        return

    occupied = _occupied_by_channels()
    for channel_index in new_indices:
        _sync_new_channel(channel_index, occupied)


def OnInit():
    global _pending_channel_scan, _pending_pattern_scan
    global _loading_project, _initialized
    _pending_channel_scan = False
    _pending_pattern_scan = False
    _loading_project = False
    _initialized = False
    _capture_baseline()
    _initialized = True


def OnDeInit():
    global _pending_channel_scan, _pending_pattern_scan, _initialized
    _pending_channel_scan = False
    _pending_pattern_scan = False
    _initialized = False


def OnProjectLoad(status):
    global _loading_project, _pending_channel_scan, _pending_pattern_scan

    if status == getattr(midi, "PL_Start", -999):
        _loading_project = True
        _pending_channel_scan = False
    elif status in (
        getattr(midi, "PL_LoadOk", -998),
        getattr(midi, "PL_LoadError", -997),
    ):
        _loading_project = False
        _capture_baseline()
        _pending_channel_scan = False
        _pending_pattern_scan = False


def OnDirtyChannel(index, flag=0):
    global _pending_channel_scan
    _pending_channel_scan = True


def OnRefresh(flags):
    global _pending_channel_scan, _pending_pattern_scan
    if flags & getattr(midi, "HW_ChannelEvent", 65536):
        _pending_channel_scan = True
    if flags & getattr(midi, "HW_Dirty_Patterns", 1024):
        _pending_pattern_scan = True


def OnIdle():
    global _pending_channel_scan, _pending_pattern_scan, _last_active_pattern

    if not _initialized or _loading_project:
        return

    # Always scan identities. This catches a deletion followed by an addition
    # even when the total Channel Rack count stays the same.
    _pending_channel_scan = False
    _scan_for_channel_changes()

    try:
        active_pattern = int(patterns.patternNumber())
    except Exception:
        active_pattern = None

    if _pending_pattern_scan or active_pattern != _last_active_pattern:
        _pending_pattern_scan = False
        _sync_active_pattern_color()
