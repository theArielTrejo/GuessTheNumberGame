## 2 Ways to set up a Network Tunnel
 ### 1. THIS ONLY WORKS ON HOME NETWORKS, UTRGV ISOLATES NETWORKS FROM EACHOTHER FOR SECURITY REASONS
A quick how to guide on how to set up a network tunnel using GuessTheNumberGame as an example...

1. Uploading your code to your virtual machine
  - scp -r /path/to/your/local/folder VMusername@VMIP:/path/to/your/remote/destination
      - Paste the command on your terminal with the correct information
  - 'scp' is Secure Copy Protocol, this protocols copies your folder onto the VM
  - '-r' recursively copyies the folder and its contents
  - '/path/to/your/local/folder' this is the destination path of your folder location
  - '/path/to/your/remote/destination' this is the location on where your want your folder to be
      - If you do not have a location, you can simply create one like a folder to store in your VM.

2. SSH into your Azure VM & Forward the port to your laptop
  - ssh -i C:\Path\to\.ssh\key\key.pem -L 0.0.0.0:8080:localhost:5002 VMusername@VMIP
      - Your laptop uses port 8080 to point to the Azure VM's port 3000
  - You can find your IP by opening up terminal and entering 'ipconfig'
  - Make sure you allow your firewall to access incoming connections on port 8080
    - You can do this by going to Azure, then VM, then network settings
  - What is happening is your computer is saying...
    - If I get data from port 8080 send the data to localhost with port 5002 on my Virtual Machine
3. You are all done! Quick and Easy
  - Debugging:
    - Run sudo lsof -i -P -n | grep LISTEN
      - This listens to ports in your VM and shows you if they are running


    - Try accessing your application through your phone by entering the IP and port
      - http://yourIP:8080 

 ### 2. THIS ALLOWS ANY NETWORK TO JOIN THE WEBSITE
 1. Install Node.js
    - Localtunnel is a free open-source library that allows you to expose a local server to the internet. It creates a secure tunnel from your local machine to a public accessible URL.
    - If you are using your personal computer, download & install Node.js from the official website.
    - If you are on your VM, to download Node.js, enter this prompt: sudo apt install nodejs npm
 2. Install LocalTunnel
    - Enter this prompt: npm install -g localtunnel
 3. Set up your url with custom subdomain
    - lt --port 5002 --subdomain myapp
    - A url will generate and show, something like this: https://myapp.loca.lt
 4. Enter the URL & Password
    - Localtunnel enforces you to enter the password to enter the website to enforce security.
    - Usually the password is the IP of your computer or your VM
    - Only one edge device per network is required to enter the password.
      
 You are now all set!
