# Launch Flow

The full sequence from CLI arguments to game session.

## States

### Dry Run
1. Parse args
2. Load config
3. Validate prefixes
4. Print summary
5. Exit 0

### CLI Command
1. Parse args
2. Detect CLI commands
3. Dispatch to handler (config/prefix/cache/version)
4. Print result
5. Exit 0 or 1

### Launch
1. Parse args
2. Resolve prefix via SettingsManager
3. Scan prefix + validate prefix DB
4. Install/sync Wand.exe (unless custom)
5. Start IPC server (TCP, random port)
6. Find monitor binary
7. Build monitor command:
   - With game tools (Steam chain): `[tools...] + [monitor, --port, PORT]`
   - Standalone Windows PE: `[wine, monitor, --port, PORT]`
   - Bare binary: `[monitor, --port, PORT]`
8. Start monitor subprocess with `WINEPREFIX` env
9. Write error fallback (status: pending)
10. Send LaunchConfig via IPC (Wand process + game process)
11. Wait for TCP connection (with timeout)
12. Wait for session_complete event (with timeout)
13. Handle timeout → run troubleshooter if enabled
14. Handle non-zero exit → run troubleshooter if enabled
15. Send shutdown to monitor
16. Wait for monitor exit (with timeout, kill if needed)
17. Return exit code

## Sequence Diagram

```
Launcher                       Monitor                    Wand         Game
   │                              │                         │           │
   ├─ start TCP listen ───────────┤                         │           │
   │                              │                         │           │
   ├─ start monitor ─────────────►│                         │           │
   │                              │                         │           │
   │◄──── TCP connect ────────────┤                         │           │
   │                              │                         │           │
   ├─ send LaunchConfig ─────────►│                         │           │
   │                              ├─ start Wand.exe ───────►│           │
   │                              │                         │           │
   │◄── process_started ──────────┤                         │           │
   │                              ├─ start game.exe ────────┤──────────►│
   │                              │                         │           │
   │◄── process_started ──────────┤                         │           │
   │                              │        (game runs...)   │           │
   │                              │                         │           │
   │◄── session_complete ─────────┤                         │           │
   │                              │                         │           │
   ├─ send shutdown ─────────────►│                         │           │
   │                              ├─ exit                   │           │
   │◄── monitor exited ───────────┤                         │           │
   │                              │                         │           │
   └─ return exit code ───────────┘                         └───────────┘
```
