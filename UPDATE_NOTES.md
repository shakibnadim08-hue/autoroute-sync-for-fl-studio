# AutoRoute Sync for FL Studio — Cleanup Update

This update fixes managed mixer inserts that kept an effect plugin after their source Channel Rack channel was deleted.

When AutoRoute Sync confirms that an automatically managed channel is gone, it now selects the owned mixer insert, focuses each occupied FX slot, verifies FL Studio’s encoded focused form ID against the exact track-and-slot plugin ID, moves keyboard focus back to the Mixer, invokes FL Studio’s own Delete command, verifies the slot is empty, and then restores the insert’s original name and color. A verified retry is allowed only for the same slot if the first Delete is delayed by focus transfer.

The cleanup is intentionally limited to mixer inserts owned by AutoRoute Sync. It does not scan or clear unrelated mixer tracks. If the running FL Studio version does not expose the verified focus and Delete path, the script leaves the plugin untouched instead of risking deletion from the wrong track.

## Update

Replace the existing file at:

```text
Documents\\Image-Line\\FL Studio\\Settings\\Hardware\\AutoRouteSync\\device_AutoRouteSync.py
```

with the updated `device_AutoRouteSync.py` from this package. FL Studio can reload the script from its MIDI Settings/script interface; no project changes are required.
