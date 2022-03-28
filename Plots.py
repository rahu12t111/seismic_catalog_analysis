import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import subprocess
import numpy as np
import math, os
import seaborn as sns
import copy
from scipy.stats import norm
from multiprocessing import Pool

def analysis(file_name):
    #selecting rows which contains our data.
    final_data = pd.read_csv("{file}.csv".format(file=file_name),sep='|')
    # print(data.head())

    #converting Date Time to proper format.
    final_data['Date Time'] = pd.to_datetime(final_data['Date Time']).dt.tz_localize(None)

    #axis=1 to remove column and axis=0 to remove row
    final_data["depth"]=[float(i) for i in final_data["depth"].to_list()]


    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    #1) ********************** 2D histogram **************************************************
    #using matplotlib fo get a 2D histogram.
    #extracting year from the Date Time column.
    year_list=final_data['Date Time'].dt.year

    list_of_pixels=[]
    #iterating over all possible magnitudes.
    for start_mag in np.arange(max(final_data['magnitude'].tolist()),min(final_data['magnitude'].tolist())-0.1,-0.1):
        list_of_pixel_row=[]
        a_data=final_data.loc[final_data["magnitude"]>start_mag]
        b_data=a_data.loc[start_mag+1>=a_data["magnitude"]]
        #iterating over all possiblw year range.
        for start_year in range(min(year_list),max(year_list)):
            initial_time=pd.to_datetime('{0}'.format(start_year)).tz_localize(None)
            final_time=pd.to_datetime('{0}'.format(start_year+1)).tz_localize(None)
            c_data=b_data.loc[b_data["Date Time"]>initial_time]
            d_data=c_data.loc[final_time>=c_data["Date Time"]]

            #appending count to list of pixels for a particular row or magnitude
            list_of_pixel_row.append(len(d_data['magnitude'].tolist()))

        #converting count list to log count list.
        list_of_log_count=[]
        for i in list_of_pixel_row:
            if i==0:
                list_of_log_count.append(0)
            else:
                list_of_log_count.append(math.log10(i))
        list_of_pixel_row=list_of_log_count
        list_of_pixels.append(list_of_pixel_row)

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8]) # main axes
    factor=(max(year_list)-min(year_list))/(max(final_data['magnitude'].tolist())-min(final_data['magnitude'].tolist()))
    plot=ax.imshow(list_of_pixels, cmap='inferno',extent=[min(year_list),max(year_list),(8/10)*factor*min(final_data['magnitude'].tolist()),(8/10)*factor*max(final_data['magnitude'].tolist())], interpolation='nearest',alpha=1)
    ax.set_xlabel('year')
    ax.set_ylabel('magnitude')
    ax.set_title('2D hist plot')
    # ax.set_xticks([0,2,4,6])
    # ax.set_xticklabels(['zero','two','four','six'])
    ax.set_yticklabels([float('{:.1f}'.format(i)) for i in np.arange(min(final_data['magnitude'].tolist()),0.1+max(final_data['magnitude'].tolist()),(max(final_data['magnitude'].tolist())-min(final_data['magnitude'].tolist()))/(len(plt.yticks()[0])-1))])
    plt.colorbar(plot).ax.set_xlabel('\nlog10(count)', rotation=0)
    plt.savefig("analysis_{region}_2D_hist_plot".format(region=region_name))
    plt.clf()


    #2)  ***************** log(count of magnitude<=cutoff for time < x) ***********************************************

    list_of_a=[1+min(final_data['magnitude'].tolist()),2.5+min(final_data['magnitude'].tolist()),4+min(final_data['magnitude'].tolist())]
    list_of_colors=['red','blue','black']
    for a in list_of_a:
        start_year=min(year_list)
        x=[]
        y=[]
        _data=final_data.loc[final_data["magnitude"] <= a]
        while start_year<=2021:
            final_time=pd.to_datetime('{0}'.format(start_year+1)).tz_localize(None)
            a_data=_data.loc[_data["Date Time"]<=final_time]
            y.append(len(a_data['magnitude'].tolist()))

            x.append(start_year)
            start_year=start_year+1

        list_of_log_count=[]
        for i in y:
            if i==0:
                list_of_log_count.append(0)
            else:
                list_of_log_count.append(math.log10(i))
        y=list_of_log_count
        plt.scatter(x,y,color="{0}".format(list_of_colors[list_of_a.index(a)]),label='cutoff = {0}'.format(a),s=9.0,alpha=1)
    plt.xlabel("Time")
    plt.ylabel("Log(Count)")
    plt.legend()
    plt.title("magnitude<=cutoff VS time")
    plt.savefig("analysis_{file}_time_vs_log(count_mag_lessthen_cutoff)".format(file=file_name))
    plt.clf()

    #3) ***************** count of magnitude<=cutoff for time < x ***********************************************

    mag_range=max(final_data['magnitude'].tolist())-min(final_data['magnitude'].tolist())
    list_of_a=[min(final_data['magnitude'].tolist()),mag_range*(1/3)+min(final_data['magnitude'].tolist()),mag_range*(2/3)+min(final_data['magnitude'].tolist()),mag_range+min(final_data['magnitude'].tolist())]
    list_of_colors=['red','blue','black']
    for i in range(len(list_of_a)-1):
        start_year=min(year_list)
        x=[]
        y=[]
        __data=final_data.loc[final_data["magnitude"] <= list_of_a[i+1]]
        _data=__data.loc[__data["magnitude"] > list_of_a[i]]
        while start_year<=2021:
            final_time=pd.to_datetime('{0}'.format(start_year+1)).tz_localize(None)

            a_data=_data.loc[_data["Date Time"]<=final_time]
            y.append(len(a_data['magnitude'].tolist()))

            x.append(start_year)
            start_year=start_year+1

        # list_of_log_count=[]
        # for i in y:
        #     if i==0:
        #         list_of_log_count.append(0)
        #     else:
        #         list_of_log_count.append(math.log10(i))
        # y=list_of_log_count
        plt.scatter(x,y,color="{0}".format(list_of_colors[list_of_a.index(list_of_a[i])]),label='cutoff = {0:.2f}'.format(list_of_a[i+1]),s=9.0,alpha=1)
        plt.xlabel("Time")
        plt.ylabel("Count")
        plt.legend()
        plt.title("magnitude<= cutoff VS time")
        plt.savefig("analysis_{file}_time_vs_(count_mag_lessthan_cutoff).jpeg".format(file=file_name))
        plt.clf()


    #4) ***************** count of magnitude<=cutoff for time < x ***********************************************

    mag_range=max(final_data['magnitude'].tolist())-min(final_data['magnitude'].tolist())
    list_of_a=[min(final_data['magnitude'].tolist()),mag_range*(1/3)+min(final_data['magnitude'].tolist()),mag_range*(2/3)+min(final_data['magnitude'].tolist()),mag_range+min(final_data['magnitude'].tolist())]
    list_of_colors=['red','blue','black']
    for i in range(len(list_of_a)-1):
        start_year=min(year_list)
        x=[]
        y=[]
        __data=final_data.loc[final_data["magnitude"] <= list_of_a[i+1]]
        _data=__data.loc[__data["magnitude"] > list_of_a[i]]
        while start_year<=2021:
            final_time=pd.to_datetime('{0}'.format(start_year+1)).tz_localize(None)

            a_data=_data.loc[_data["Date Time"]<=final_time]
            y.append(len(a_data['magnitude'].tolist()))

            x.append(start_year)
            start_year=start_year+1

        # list_of_log_count=[]
        # for i in y:
        #     if i==0:
        #         list_of_log_count.append(0)
        #     else:
        #         list_of_log_count.append(math.log10(i))
        # y=list_of_log_count
        plt.scatter(x,y,color="{0}".format(list_of_colors[list_of_a.index(list_of_a[i])]),label='cutoff = {0:.2f}'.format(list_of_a[i+1]),s=9.0,alpha=1)
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.legend()
    plt.title("magnitude<= cutoff VS time")
    plt.savefig("analysis_{file}_time_vs_(count_mag_lessthen_cutoff).jpeg".format(file=file_name))
    plt.clf()


    #5) ********************* kernel plot using sns **************************************************
    #*****1D******
    sns.distplot(a=final_data['magnitude'], color='purple', axlabel="magnitude",norm_hist=True , rug=True, kde=True, kde_kws={"color": "k", "lw": 1, "label": "KDE"}, rug_kws={"color": "g"},hist=True,bins=25,hist_kws={"edgecolor": 'black'})
    plt.title('1D kernel density plot')
    plt.savefig("analysis_{file}_1D_density_plot".format(file=file_name))
    plt.clf()

    #*****1D in log scale******
    sns.distplot(a=final_data['magnitude'], color='purple', axlabel="magnitude",norm_hist=True , rug=True, kde=True, kde_kws={"color": "k", "lw": 1, "label": "KDE"}, rug_kws={"color": "g"},hist=True,bins=25,hist_kws={"edgecolor": 'black',"log":"True"})
    plt.title('1D log kernel density plot')
    plt.savefig("analysis_{file}_1D_log_density_plot".format(file=file_name))
    plt.clf()

    #********** for log10(count>mag.) *****************************************************************
    list_of_number=(final_data['magnitude']).tolist()
    copy_list_of_number=list_of_number[:]
    unique_list=[]
    final_list=list_of_number

    for i in final_list:
        if i not in unique_list:
            unique_list.append(i)
    unique_list.sort()

    count_list=[copy_list_of_number.count(i) for i in unique_list]

    final_count=len(list_of_number)

    count=0
    cumulative_count_list=[]
    for i in count_list:
        end_count=final_count-count
        cumulative_count_list.append(end_count)
        count=count+i
    log_cumulative_count_list=[math.log10(i) for i in cumulative_count_list]
    plt.scatter(x=unique_list,y=log_cumulative_count_list,s=1,color="purple",alpha=1)
    plt.xlabel("mag.")
    plt.ylabel("log(count>=mag)")
    plt.title("mag vs log(cumulative_count)")
    plt.savefig("analysis_{file}_mag_vs_log(cumulative_count)".format(file=file_name))
    plt.clf()


    #********** for log10(count) *****************************************************************
    list_of_number=(final_data['magnitude']).tolist()
    copy_list_of_number=list_of_number[:]
    unique_list=[]
    final_list=list_of_number

    for i in final_list:
        if i not in unique_list:
            unique_list.append(i)

    count_list=[copy_list_of_number.count(i) for i in unique_list]
    log_count_list=[math.log10(i) for i in count_list]
    plt.scatter(x=unique_list,y=log_count_list,s=1,color="black",alpha=1)
    plt.xlabel("mag.")
    plt.ylabel("log(count)")
    plt.title("mag vs log count")
    plt.savefig("analysis_{file}_mag_vs_log(count)".format(file=file_name))
    plt.clf()


    #***************** count of mag. <=5 with time ***********************************************
    start_year=1900
    x=[]
    y=[]
    _data=final_data.loc[final_data["magnitude"] <= 4]
    while start_year<=2021:
        initial_time=pd.to_datetime('{0}-01-01T00:00:00.0Z'.format(start_year)).tz_localize(None)
        final_time=pd.to_datetime('{0}-01-01T00:00:00.0Z'.format(start_year+1)).tz_localize(None)
        a_data=_data.loc[_data["Date Time"]>initial_time]
        b_data=a_data.loc[final_time>=a_data["Date Time"]]
        y.append(len(b_data['magnitude'].tolist()))
        x.append(start_year)
        start_year=start_year+1
    plt.bar(x,y,color="brown",width = 0.4)
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.title("mag. <= 5 VS time")
    plt.savefig("analysis_{file}_time_vs_mag_lessthen_5".format(file=file_name))
    plt.clf()


    # #***************** kernel plot plotly *********************************************************
    # #plotting histogram for mag.
    # #kernal plot.
    # hist_data = [final_data["mag."]]
    # group_labels = ['distplot'] # name of the dataset
    # fig = ff.create_distplot(hist_data, group_labels, bin_size=[.1])
    # fig.write_image('analysis_mag.png')
    # plt.clf()


    #********************* kernel plot using sns **************************************************
    #*****1D******
    sns.distplot(a=final_data['magnitude'], color='purple', axlabel="magnitude", rug=True, kde=True, kde_kws={"color": "k", "lw": 1, "label": "KDE"}, rug_kws={"color": "g"},hist=True,bins=50,hist_kws={"edgecolor": 'black'})
    plt.title('1D kernel density plot')
    plt.savefig("analysis_{file}_1D_density_plot".format(file=file_name))
    plt.clf()

    sns.distplot(a=final_data['magnitude'], fit=norm, color='purple', axlabel="magnitude", rug=True, kde=False, kde_kws={"color": "k", "lw": 1, "label": "KDE"}, rug_kws={"color": "g"},hist=True,bins=50,hist_kws={"edgecolor": 'black'})
    plt.title('1D normal density plot')
    plt.savefig("analysis_{file}_1D_normal_density_plot".format(file=file_name))
    plt.clf()

    #*****2D******
    sns.kdeplot(x=final_data['Date Time'], y=final_data['magnitude'], color='b',shade=True, fill=False, label='mag. density plot',cmap="mako", cbar=True, thresh=0.01)#one more parameter can be added => shade_lowest=True
    plt.legend()
    plt.title("2D mag. density plot")
    plt.savefig("analysis_{file}_2D_density_plot".format(file=file_name))
    plt.clf()


    #********************** data info ***********************************************************
    file= open('analysis_{file}_info.csv'.format(file=file_name),'a')
    file.writelines(['Total number of entries = {0}'.format(len(final_data['magnitude'].tolist()))+'\n'+ 'number of columns={0}'.format(len(list(final_data.columns)))+'\n'+'{0}'.format(list(final_data.columns))+'\n\n',
                    'parameter,minimum value,maximum value'+'\n',
                    'Date Time,{0},{1}'.format(min(final_data['Date Time']),max(final_data['Date Time']))+'\n',
                    'magnitude,{0},{1}'.format(min(final_data['magnitude']),max(final_data['magnitude']))+'\n',
                    'depth,{0},{1}'.format(min(final_data['depth']),max(final_data['depth']))+'\n'])
    file.close()

    #plotting mag. vs time.
    plt.scatter(final_data['Date Time'],final_data["magnitude"],s=1,color="red",alpha=1)
    plt.xlabel("Time")
    plt.ylabel("mag.")
    plt.title("mag. VS time")
    plt.savefig("analysis_{file}_time_vs_mag".format(file=file_name))
    plt.clf()


    #plotting depth vs time.
    plt.scatter(final_data['Date Time'],final_data["depth"],s=1,color="green",alpha=1)
    plt.xlabel("Time")
    plt.ylabel("depth")
    plt.title("depth VS time")
    plt.savefig("analysis_{file}_time_vs_depth".format(file=file_name))
    plt.clf()


    #plotting mag. vs depth.
    plt.scatter(final_data["depth"],final_data["magnitude"],s=1,color="blue",alpha=1)
    plt.xlabel("depth")
    plt.ylabel("mag.")
    plt.title("mag. VS depth")
    plt.savefig("analysis_{file}_mag_vs_depth".format(file=file_name))
    plt.clf()


    #plotting histogram.
    #for mag.
    plt.hist(final_data["magnitude"],bins=500)
    plt.xlabel("mag.")
    plt.title("mag. histogram")
    plt.savefig("analysis_{file}_mag".format(file=file_name))
    plt.clf()

    #for depth.
    plt.hist(final_data["depth"],bins=500)
    plt.xlabel("depth")
    plt.title("depth histogram")
    plt.savefig("analysis_{file}_depth".format(file=file_name))
    plt.clf()

    #profiling the data.
    from pandas_profiling import ProfileReport
    prof = ProfileReport(final_data)
    prof.to_file(output_file='analysis_{file}_profile.html'.format(file=file_name))

    #creating a column for size of the scatter markers according to magnitude.
    final_data["size"]=[math.exp(i) for i in final_data["magnitude"]]

    import plotly.graph_objects as go
    import plotly.figure_factory as ff

    fig = px.scatter_mapbox(final_data, lat="latitude", lon="longitude", size="size", color="depth", color_continuous_scale=[(0, "red"), (0.5, "green"), (1, "blue")], opacity=0.7 , range_color=[0,250], hover_data=["Date Time","latitude","longitude","depth","magnitude"], zoom=3, height=900)
    fig.update_layout(mapbox_style="stamen-terrain", showlegend=True, mapbox_zoom=1,margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html("analysis_{region}_map.html".format(region=region_name))
    fig.show()

    subprocess.run(['mkdir Analysis | chmod -R 775 analysis | mv -f analysis_* Analysis/'],shell=True,timeout=None,check=True,capture_output=False)

# INPUT
file_name = input('Enter file name to be anlysed (file should be present in same directory) :')
# Starting analysis.
analysis(file_name)
