import subprocess

print("This will open 4 gnome terminals")

command = ['gnome-terminal','--tab','-e',"python3 chord.py 3000",'--tab','-e',"python3 chord.py 3500 3000",'--tab','-e',"python3 chord.py 4500 3000",'--tab','-e',"python3 chord.py 5000 3000"]
subprocess.run(command)