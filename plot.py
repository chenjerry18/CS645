import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from pylab import plot, show, savefig, xlim, figure, hold, ylim, legend, boxplot, setp, axes
def setBoxColors(bp):
    setp(bp['boxes'][0], color='blue')
    setp(bp['caps'][0], color='blue')
    setp(bp['caps'][1], color='blue')
    setp(bp['whiskers'][0], color='blue')
    setp(bp['whiskers'][1], color='blue')
    setp(bp['fliers'][0], color='blue')
    setp(bp['fliers'][1], color='blue')
    setp(bp['medians'][0], color='blue')

    setp(bp['boxes'][1], color='red')
    """
    setp(bp['caps'][2], color='red')
    setp(bp['caps'][3], color='red')
    setp(bp['whiskers'][2], color='red')
    setp(bp['whiskers'][3], color='red')
    setp(bp['fliers'][2], color='red')
    setp(bp['fliers'][3], color='red')
    setp(bp['medians'][1], color='red')
    """
def plot_line(ins, values, title, xlabel, ylabel, filename):
    plt.figure(2, figsize=(6,4))
    plt.plot(ins,values,'o-')
    plt.grid(True)
    plt.title(title)  
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig("../Figures/" + filename + ".pdf")
    #plt.show()
    plt.clf()
    plt.close()


def plot_doubleline(ins, values, title, xlabel, ylabel, filename, labels):
    plt.figure(2, figsize=(6,4))
    plt.plot(ins,values[:,0],'sb-')
    plt.plot(ins,values[:,1],'or-')    
    plt.grid(True)
    plt.title(title)  
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(labels,loc="best")
    plt.tight_layout()
    plt.savefig("./" + filename + ".pdf")
    plt.show()
    plt.clf()
    plt.close()

def plot_box(ins, random, suggest, title, xlabel, ylabel, filename, labels):
    #print suggest
    dimension = len(ins)
    #print dimension, len(random)
    fig = plt.figure(2, figsize=(6,4))
    ax = axes()
    hold(True)
    pos = [1, 2]
    x_limit = 6
    limit = min(dimension, x_limit)
    for i in range(limit):
        data = []
        data.append(random[i])
        data.append(suggest[i])
        data_trans =  np.asarray(data).reshape(len(random[i]), 2)
        #data_trans = np.asarray(data)
        #print data_trans, data
        dp = plt.boxplot(data_trans, positions = pos, widths = 0.6)
        setBoxColors(dp)
        pos[0] += 2
        pos[1] += 2
        i += 1
    #plt.tight_layout()
    plt.xlim(0,limit)
    plt.ylim(0,0.01)
    ax.set_xticklabels(ins)
    xticks = [1.5 + 2* x for x  in range(limit + 1)]
    print xticks
    ax.set_xticks(xticks)
    
    # draw temporary red and blue lines and use them to create a legend
    hB, = plot([1,1],'b-')
    hR, = plot([1,1],'r-')
    legend((hB, hR),('random', 'autoCompletion'))
    hB.set_visible(False)
    hR.set_visible(False)
    
    plt.savefig("./" + filename + ".pdf")
    plt.show()
    plt.clf()
    plt.close()      

    
def plot_box1(ins, values, title, xlabel, ylabel, filename, labels):

    labels = ins.tolist()
    fs = 10  # fontsize   
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(6, 6), sharey=True)
    axes[0, 0].boxplot(values[:,0], labels=labels)
    axes[0, 0].set_title('Random', fontsize=fs)
    
    axes[0, 0].boxplot(values[:,1], labels=labels)
    axes[0, 0].set_title('Random', fontsize=fs)    
    """
    boxprops = dict(linestyle='--', linewidth=3, color='darkgoldenrod')
    flierprops = dict(marker='o', markerfacecolor='green', markersize=12,
                      linestyle='none')
    medianprops = dict(linestyle='-.', linewidth=2.5, color='firebrick')
    meanpointprops = dict(marker='D', markeredgecolor='black',
                          markerfacecolor='firebrick')
    meanlineprops = dict(linestyle='--', linewidth=2.5, color='purple')
    fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(6, 6), sharey=True)
    axes[0, 2].boxplot(values[:,1], whis='range')
    axes[0, 2].set_title('whis="range"', fontsize=fs)
   
    axes[0, 0].boxplot(values[:,1], labels=labels)
    axes[0, 0].set_title('Default', fontsize=fs) 
    
    for ax in axes.flatten():
        ax.set_yscale('log')
        ax.set_yticklabels([])

    fig.suptitle("I never said they'd be pretty")
    fig.subplots_adjust(hspace=0.4)
    plt.show()
    """