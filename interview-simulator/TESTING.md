# Verification record

## Executed during project creation

- Compiled all core Java sources with the Java 17 compiler module.
- Started the real JDK HTTP server and served the application assets.
- Ran `python3 tests/integration.py` against isolated real HTTP servers.
- Verified account creation, login, cookie authentication and logout.
- Completed all five questions and verified persisted feedback and history.
- Restarted the Java process and confirmed saved accounts and completed history remain available.
- Verified cross-account reads/writes fail, anonymous requests fail and cross-origin mutations fail.
- Verified answer length validation, duplicate submission and conflicting idempotency keys.
- Verified that AI mode cannot be selected when it has no server-side configuration.
- Tested the AI HTTP adapter against a controlled local provider stub: malformed output, saved failure state, retry recovery and duplicate retry rejection. This is not a test of a live commercial model.
- Checked frontend JavaScript syntax with `node --check`.

## Not verified in this environment

- Visual browser QA and browser-driven end-to-end interaction. No browser executable was available, and the browser installation download could not complete.
- The Docker/Tomcat/MySQL stack and the Maven WAR build. Docker and Maven were unavailable; external dependency downloads could not complete.
- A real AI-provider account, voice recognition and microphone permissions.

These limits are explicit; passing the Java HTTP tests does not establish that the other deployment adapters have been exercised.

## Checks before your presentation

1. Run `start.bat`, open localhost:8080 and create an account.
2. Start a beginner web interview. Type an answer, submit and inspect feedback.
3. Leave a draft on question two, use Save & leave, then Resume session.
4. Finish five answers. Review the summary and download the JSON record.
5. Sign out, sign back in and open My sessions.
6. Try a narrow browser window and keyboard-only navigation.
7. Run the GitHub Actions build after upload to verify WAR compilation.
8. If presenting the Servlet/MySQL stack, run Docker Compose and repeat the workflow there. That mode has separate storage.
9. If using AI, verify a real provider call before the demonstration. Keep rule-based mode available as the clearly labelled offline option.

No benchmark, automated scoring accuracy or improvement in interview outcomes is claimed.
