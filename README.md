
# cell-counter

This project aims to develop an calcium imaging-based alternative to microelectrode array (MEA) experiments to record retinal neuron activity. While MEA provides excellent temporal resolution and allows for the direct monitoring of action potentials, it lacks spatial resolution, and the source of an action potential cannot definitively be identified (it could be coming from a single neuron, or a "unit" of neurons acting in unison). Ca<sup>2+</sup> influx is an indirect indicator of action potentials ([Grienberger & Konnerth, 2012](https://www.cell.com/neuron/fulltext/S0896-6273(12)00172-9)), so utilizing two-photon microscopy and fluorescent calcium indicators can provide high-fidelity spatial information with high, although not equivalent to MEA, level of temporal resolution. 


Currently in a very rudimentary stage, GUI refinements and added features coming soon!

<u>**How to run:**</u>

Clone or download the repo, and follow the instructions for your respective platform.

Mac/Linux: Enter the following into your Terminal.
`python main.py`

Windows: Enter the following into Command Prompt.
`py main.py`

<u>**TODO:**</u>
- Add more documentation
- Integrate breadth-first search from previous code to map dendritic connections
- Link to ImageJ for tracking photoswitching index and add to result JSON
- Optimize runtimes—there are currently too many unnecessary loops
- Create executables/applications for each platform (Mac .app/Windows .exe\*) for command-line averse users

<u>**Screenshots:**</u>

Import Screen:

![import screen](https://i.imgur.com/TFPOL8y.png)

Result Screen:

![result screen](https://i.imgur.com/liLCy6w.png)

At the moment, the results screen isn't too exciting, but experimentation in a Jupyter Notebook using breadth-first search yielded this:

![eda](https://i.imgur.com/Dr7bNMq.png)

The green represents a dendritic connection between the somas of two cells, and merging the BFS code from the Jupyter notebook is the next step so that this program can generate the same.

\
\
\
\
\
\
\
\* If you're using Linux, I doubt you need an executable to click on :)
