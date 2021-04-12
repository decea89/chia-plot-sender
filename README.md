# chia-plot-sender
Controller to send plots from plotter to farmer via LAN. Plotter and Farmer are two different machines (ubuntu) connected via LAN. 
Whenever plotter finishes a plot file, this is stored in a local plotter path. plotSender.py keeps looking at that local plotter path in order to send the plot files
to several paths at your farmer machine, so that, chia farmer can use these new plots. plotSender.py can send several plots at once by using the concurrence parameter. 

First at all, edit the plotSender.py to change the paths string.

Example of usage with concurrence ( 3 plots being sent to 3 different paths parallely ):

  python3 plotSender.py 3

If you don't type a parameter like below, plotSender.py use the maximun concurrence level possible (if you have 4 destiny paths, it will send 4 plots parallely) :

  python3 plotSender.py


