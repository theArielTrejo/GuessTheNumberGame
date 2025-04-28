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

