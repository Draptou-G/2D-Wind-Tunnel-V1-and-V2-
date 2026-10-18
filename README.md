# 2D-Wind-Tunnel-V1-and-V2-
My project is a simulated wind tunnel, and how objects interact with fluids using python. It simulates fluids on a 2D plane and calculates density, pressure and velocity. There is also some variables you can play around with like wind speed().
V1 is a way more simpler version than V2.


**Requirements:**
Python 3
NumPy
Matplolib
These are all in the requirementV2.txt already.
Vs code

**Method one
Terminal**

**Installation**
Download the files

you need to make a virtual internment,
to do that just open terminal and type:

python3 -m venv .venv

For linux/mac:
source .venv/bin/activate

Windows:
.venv\Scripts\activate

next install the required packages:
pip install -r requirements.txt

**Open the simulation:**
Type: python3 wind-tunnel.py for V1
Type: python3 windtunnelV2.py for V2


**Method 2, Virtual studio code(VS code)**

If you don't have VS code download it from their website:
https://code.visualstudio.com/download?_exp_download=d53503e735

Then make sure you have python libraries installed
Go to extensions and then search for Python by Mircrosoft
Make sure they are active

Go to select file and open folder then selec the either the v1 or v2 folder(not both at the same time)

Note only V2 needs this step if you want to run V1 you can.

Then got to terminal on the top bar and select new terminal

Then type in the terminal:
python -m venv .venv
python -m pip install -r requirementsV2.txt

Press ctrl shift p or cmd shift-p
slect python interpreter and choose the .venv folder 

Final you should see a play button on the top right of the code and click run.

