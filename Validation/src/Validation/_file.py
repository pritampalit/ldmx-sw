"""Wrap an uproot file for some extra help plotting"""

import uproot
import os

class File :
    """File entry in Differ object

    Parameters
    ----------
    filepath : str or pathlib.Path
        path specifying ROOT file to open for reading
    legendlabel : str
        name for labeling histograms plotted from this file
    colmod : function with str argument returning str
        modify an input column name to align with the columns in this file
        can be used for example to change the pass name
    hist_kwargs : dict
        dictionary providing extra detail for the matplotlib hist call
        helpful for specifying style options and other defaults for hists from this file
    open_kwargs : dict
        all other key-word arguments are passed to uproot.open
    """

    def __init__(self, filepath, legendlabel, colmod = None, hist_kwargs = dict(), **open_kwargs) :
        self.__file = uproot.open(filepath, **open_kwargs)
        self.__legendlabel = legendlabel
        self.__colmod = colmod
        self.__df = None

        if 'histtype' not in hist_kwargs :
            hist_kwargs['histtype'] = 'step'
        if 'linewidth' not in hist_kwargs :
            hist_kwargs['linewidth'] = 2
        if 'label' not in hist_kwargs :
            hist_kwargs['label'] = self.__legendlabel
        if 'bins' not in hist_kwargs :
            hist_kwargs['bins'] = 'auto'
            
        self.__hist_kwargs = hist_kwargs

    def from_path(filepath, legendlabel_parameter = None) :
        """Extract the legend-label for histograms from this file using the filepath

        This is separated from the contsructor because

        1. It makes assumptions on how the file name is formatted
        2. It does not allow for modification of the keyword args in the constructor

        The parameters of a file are extracted from its name.
        In general, we assume that the filename is of the form

        <key1>_<val1>_<key2>_<val2>_...<keyN>_<valN>.root

        i.e. a mapping where the key/val pairs are separated by underscores.

        If the 'legendlabel_parameter' is not provided, we simply use the first key-val
        pair in the file name as the legend-label.

        Parameters
        ----------
        filepath : str
            Full path to the file to open
        legendlabel_parameter : str, optional
            key-name to use in legend-label for this File
        """
        l = os.path.basename(filepath).replace('.root','').split('_')
        file_params =  { l[i] : l[i+1] for i in range(len(l)) if i%2 == 0 }
        
        legendlabel = next(iter(file_params))
        if legendlabel_parameter is not None :
            if legendlabel_parameter in file_params :
                file_params[legendlabel_parameter]
            else :
                raise KeyError(f'{legendlabel_parameter} not in deduced file parameters\n{file_params}')

        return File(filepath, legendlabel)

    def keys(self, *args, **kwargs) :
        """Callback into uproot keys

        Helpful for exploring the file when trying to decide
        what to plot within a notebook
        """
        return self.__file.keys(*args, **kwargs)

    def is_events(self) :
        """Check if this file is an Events file
        
        We simply see if the 'LDMX_Events' object exists within
        the file. If it does, we assume that it is an event file.
        Otherwise, we assume that it is a histogram file.
        """
        return 'LDMX_Events' in self.__file
    
    def events(self, **kwargs) :
        """Callback for retrieving a full in-memory data frame of the events
        
        All key-word arguments are passed to the uproot.arrays method.
        
        We change the default 'library' to be pandas which can be overridden
        by a user if desired.
        """

        if 'library' not in kwargs :
            kwargs['library'] = 'pd'
        return self.__file['LDMX_Events'].arrays(**kwargs)
    
    def load(self, manipulation = None, **kwargs) :
        """Instead of giving the events data frame to the caller,
        we store the dataframe here for later batch processing
        
        manipulation is a function operating on the loaded dataframe
        which is there for people to rename columns, calculate new
        columns, etc...
        
        All the kwargs are simply provided to events for selecting
        the branches of LDMX_Events to load into memory.
        """
        self.__df = self.events(**kwargs)
        if manipulation is not None :
            manipulation(self.__df)
    
    def manipulate(self, manipulation) :
        """Apply the passed manipulation to the dataframe"""
        manipulation(self.__df)
    
    def plot1d(self, ax, obj, **hist_kwargs) :
        """Plot the input uproot object as a histogram on the input axes

        Provided the same interface for different plotting options, all
        depending on how the input 'obj' is deduced.

        If 'obj' is not a str, we assume that is is a callable (e.g. a function)
        that will take the in-memory dataframe (if it is loaded) or the uproot file
        (if the dataframe isn't loaded) in order to calculate the array of values
        to histogram. This is helpful for doing simple calculations or cuts that
        this class does not implement.

        If 'obj' is a str, then we need to use it to deduce what we are plotting.

        If a in-memory dataframe exists, we check if 'obj' is a column in it first
        and use that column of the dataframe as the values to histogram.
        
        If no dataframe exists (or 'obj' is not in the dataframe), then we get 
        the object from the uproot file we have with 'obj' as the full in-file
        path to the object (using the configured colmod function in order to 
        augment the name if necessary).

        Now, if the uproot object is a subclass of uproot's Histogram class,
        we retrieve the bin edges from it, check that its dimension is one,
        and plot the histogram using its values as the entry weights and the
        loaded bin edges.

        If the uproot object is not a subclass of uproot's Histogram,
        then we assume that it is a branch and we extract a flattened
        array of values from it using uproot.array and pandas.

        Parameters
        ----------
        ax : matplotlib.Axes
            axes on which to plot the histogram
        obj : str or function
            object to plot
        """

        for k, v in self.__hist_kwargs.items() :
            if k not in hist_kwargs :
                hist_kwargs[k] = v
              
        if not isinstance(obj, str) :
            if self.__df is None :
                return ax.hist(obj(self.__file), **hist_kwargs)
            else :
                return ax.hist(obj(self.__df), **hist_kwargs)

        if self.__df is not None and obj in self.__df :
            return ax.hist(self.__df[obj], **hist_kwargs)
        
        uproot_obj_path = obj
        if self.__colmod is not None :
            uproot_obj_path = self.__colmod(obj)

        uproot_obj = self.__file[uproot_obj_path]

        if issubclass(type(uproot_obj), uproot.behaviors.TH1.Histogram) :
            edges = uproot_obj.axis('x').edges()
            dim = len(edges.shape)
            if dim > 1 :
                raise KeyError(f'Attempted to do a 1D plot of a {dim} dimension histogram.')
            # overwrite bins and weights with what the serialized histogram has
            hist_kwargs['bins'] = edges
            hist_kwargs['weights'] = uproot_obj.values()
            return ax.hist((edges[1:]+edges[:-1])/2, **hist_kwargs)
        else :
            return ax.hist(uproot_obj.array(library='pd').values, **hist_kwargs)
