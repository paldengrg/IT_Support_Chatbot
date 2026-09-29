# Linux: Check Network Connectivity

## Check your connection
1. Show network devices and their state: `nmcli device status`
2. Show IP addresses: `ip addr`
3. Test internet access: `ping -c 4 8.8.8.8`
4. Test name resolution: `ping -c 4 example.com`

## Interpreting the results
If step 3 works but step 4 fails, the problem is DNS. If step 3 fails, the machine has no internet access; check the cable or Wi-Fi connection.

## Restart networking
Run `sudo systemctl restart NetworkManager`. This needs administrator rights.
