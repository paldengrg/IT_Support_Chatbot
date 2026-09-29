# Windows: Reset Network Settings

## When to use this
Use these steps on Windows 10 or Windows 11 when Wi-Fi or Ethernet connects but pages will not load, or the connection keeps dropping after other fixes have failed.

## Renew the IP address and clear DNS cache
1. Click Start, type `cmd`, and open Command Prompt.
2. Run `ipconfig /release` and press Enter.
3. Run `ipconfig /renew` and press Enter.
4. Run `ipconfig /flushdns` and press Enter.
5. Close Command Prompt and try the connection again.

## Full network reset (Windows 11)
1. Open Settings > Network & internet > Advanced network settings.
2. Select Network reset, then Reset now, and confirm.
3. Your PC restarts. Reconnect to Wi-Fi and enter the password again.

## Full network reset (Windows 10)
1. Open Settings > Network & Internet > Status.
2. Select Network reset, then Reset now, and confirm.
3. Your PC restarts. Reconnect to Wi-Fi and enter the password again.

## Notes
A network reset removes saved Wi-Fi networks and VPN connections. If the company VPN stops working afterwards, contact IT Support at support@example.com.
