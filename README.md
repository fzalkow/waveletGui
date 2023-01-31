# waveletGui

## Description

This is a GUI for manipulating audio files in the wavelet domain.

## Dependencies

* [Python 3](https://www.python.org) with the following modules installed:
  * [PyQt5](https://riverbankcomputing.com/software/pyqt/download)
  * [pywt](http://www.pybytes.com/pywavelets/)
  * [numpy](http://www.numpy.org)
  * [scipy](http://www.scipy.org)

You can install all dependencies with the provided environment.yaml using [Anaconda](https://docs.conda.io/en/latest/miniconda.html).

    conda env create -f environment.yaml
    conda activate waveletGui

## Usage

Just run

    python waveletGui.py

and a GUI opens which will let you import a WAVE-file, choose a mother wavelet, edit the file in the wavelet domain and export the result to a WAVE-file again. Currently only mono files are supported.

## License

*waveletGui* is licensed under the [MIT License](http://opensource.org/licenses/MIT). This means you can do anything you want with the code as long as you provide attribution back to me.
