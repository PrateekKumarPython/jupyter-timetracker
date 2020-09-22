def track():

    import os
    import sys
    import socket
    import platform
    import datetime as dt
    import glob
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    import seaborn as sns
    import ipywidgets as widgets
    import imp
    import time
    import pickle
    import threading
    import warnings
    
    from IPython.display import display, HTML, Image, Video
    from ipywidgets import interact, interact_manual, fixed
    from ipywidgets import Label, FloatProgress, FloatSlider, Button
    from ipywidgets.widgets import Layout, HBox, VBox

    warnings.filterwarnings('ignore')

    sns.set()
    plt.rcParams.update({'font.family': 'serif', 'font.weight': 'bold'})

    info = {
        'System ': socket.gethostname(),
        'Platform': platform.platform(),
        'Python Version': sys.version,
        'Python Directory': sys.executable,
        'Current Directory': os.getcwd(),
        'Last Run': dt.datetime.now().strftime('%d %b %Y, %H:%M:%S'),
    }

    dr = {}

    cwd = os.getcwd()
    keys = ['DOC', 'EXT', 'FIG', 'MAT', 'RAW', 'REP', 'STC', 'VID']
    dr.update({k: '%s/%s/' % (cwd, k) for k in keys})
    for k in dr:
        os.makedirs(dr[k], exist_ok=True)

    dpi = 72
    Activity = [
        'Sleeping', 'Drinks', 'Refresh', 'Walk', 'Yoga', 'Gym', 'Breakfast',
        'Driving', 'Management', 'Python', 'Tea', 'Study', 'Lunch', 'Table Tennis',
        'Discussions', 'Report Writing', 'Meetings', 'Presentations',
       'Snacks', 'Stairs', 'Writing', 'Dinner','Housework', 'Family', 'Friends',
        'Meetups', 'Volleyball', 'Housework',
        'Reading non fiction', 'Reading fiction', 'Singing', 'Movie', 'TV Series',
        'YouTube', 'Music', 'Web Surfing', 'Coursera', 'Volleyball', 'Cycling',
        'Traveling', 'Shopping', 'Social Media', 'Entertainment', 'Vocabulary',
        'Thinking','News', 'Video Shooting','Video Editing','Creative Works','Chatting'
    ]

    msg = "Welcome to Time Management !\nSince this is your first time.\nYou have to manually enter your first entry and rerun the cell again to access all features."

    out_0 = widgets.Output()
    out_1 = widgets.Output()
    out_2 = widgets.Output()
    out_3 = widgets.Output()
    out_4 = widgets.Output()
    out_5 = widgets.Output()

    def sync():
        '''
        Sync the timesheets between your local and external sources. It will take no inputs, just run the function.
        It will save 2 minutes of everyday and possible mistakes
        '''

        import shutil
        import time

        if info['Platform'][:7] == 'Windows':
            ep = 'I:/Timesheet.pkl'
        elif info['System ']=='kali':
            ep = '/media/root/UUI/Timesheet.pkl'
        else:
            ep = '/media/prateek/UUI/Timesheet.pkl'

        if not os.path.exists(ep):
            print('%s does not exists ' % (ep))
            return

        lp = dr['MAT'] + 'Timesheet.pkl'

        ext = os.path.getmtime(ep)
        lcl = os.path.getmtime(lp)

        extsz=os.path.getsize(ep)
        lclsz=os.path.getsize(lp)

        print('Local    : %s  %6.2f KB' % (time.ctime(lcl),lclsz/1024.))
        print('External : %s  %6.2f KB' % (time.ctime(ext),extsz/1024.))

        if (lcl > ext) and (lclsz>extsz) :
            shutil.copy(lp, ep)
            print('Copied to external')
        elif (lcl < ext) and (lclsz<extsz) :
            shutil.copy(ep, lp)
            print('Copied to local')
        else:
            print('Already in Sync. Do manually if you do not believe so')

    def update():
        '''
        Update the timesheet from reading the atime logger csv report. Benefits :-
        Save the time spent on manual entries.
        Easily get the time spent upto the second's precision

        This process will always be performed on a local system
        '''

        fn_csv = dr['RAW'] + dt.datetime.today().strftime('report-%d-%m-%Y.csv')

        if not os.path.exists(fn_csv):
            print('%s does not exists' % (fn_csv))
            return

        aa = pd.read_csv(fn_csv)
        idx = aa[aa[aa.columns[0]] == aa.columns[0]].index[0] - 1
        aa1 = aa.loc[0:idx]
        d = read(dr['MAT'] + 'Timesheet.pkl')
        d.iloc[-1]['To']
        b = aa1[pd.to_datetime(aa1['From']) > d.iloc[-1]['To']]
        b1 = {
            'Activity': [i.rstrip() for i in b['Activity type']],
            'From': pd.to_datetime(b['From']),
            'To': pd.to_datetime(b['To']),
            'Notes': b['Comment']
        }
        b11 = pd.DataFrame(b1)
        b12 = b11.reindex(index=b11.index[::-1])
        b12['Duration'] = b12['To'] - b12['From']
        if len(b12) == 0:
            print('Data is already updated')
        else:
            print('%d entries added' % (len(b12)))
        d = pd.concat((d, b12), ignore_index=True)
        d = d.fillna('')
        d.to_pickle(dr['MAT'] + 'Timesheet.pkl')
        d.to_pickle(dr['EXT'] +
                    dt.datetime.now().strftime('Timesheet-%y%m%d-%H%M%S.pkl'))

    @out_5.capture(clear_output=True, wait=True)
    def sync_update():
        '''
        It will sync and update ( from csv) the timesheet
        '''
        sync()
        update()
        sync()
        display(read(dr['MAT'] + 'Timesheet.pkl').tail())

    @out_5.capture(clear_output=True, wait=True)
    def sync_update1(b):
        '''
        It will sync and update ( from csv) the timesheet
        '''
        sync()
        update()
        sync()
        display(read(dr['MAT'] + 'Timesheet.pkl').tail())

    def make_df(lst):
        columns = 'Activity', 'From', 'To', 'Notes'
        a = pd.DataFrame(lst, columns=columns)
        a['Duration'] = a['To'] - a['From']
        return a

    def make_df_id(lst, idx):
        columns = 'Activity', 'From', 'To', 'Notes'
        a = pd.DataFrame(lst, columns=columns, index=[idx - 0.5])
        a['Duration'] = a['To'] - a['From']
        return a


    def read(fn):
        '''
        read the saved variable using pickle library of python.
        '''
        with open(fn, 'rb') as f:
            data = pickle.load(f)
        return data


    def save(dct, fn):
        '''
        It will save the variable using pickle library
        fn : will be the output file name ( can be any .pkl is convention)
        '''
        with open(fn, 'wb') as f:
            pickle.dump(dct, f)


    def loop_1():
        while b_start[1].icon == 'stop':
            To[1].value = str(dt.datetime.today() -
                              pd.to_datetime(From[1].value))[7:-7]
            time.sleep(1)


    def loop_2():
        while b_start[2].icon == 'stop':
            To[2].value = str(dt.datetime.today() -
                              pd.to_datetime(From[2].value))[7:-7]
            time.sleep(1)


    def loop_3():
        while b_start[3].icon == 'stop':
            To[3].value = str(dt.datetime.today() -
                              pd.to_datetime(From[3].value))[7:-7]
            time.sleep(1)


    @out_0.capture(clear_output=True, wait=True)
    def stop_click(b):
        '''
        Function for Manual Time Logging
        '''
        A = Act[0].value
        From_str = From[0].value
        To_str = To[0].value
        N = Notes[0].value

        if os.path.exists(dr['MAT'] + 'Timesheet.pkl'):
            d = read(dr['MAT'] + 'Timesheet.pkl')
        else:
            d = pd.DataFrame(
                columns=['Activity', 'From', 'To', 'Notes', 'Duration'])
        F = pd.to_datetime(From_str)
        T = pd.to_datetime(To_str)
        aa = make_df([[A, F, T, N]])
        d = pd.concat((d, aa), ignore_index=True)
        d.to_pickle(dr['MAT'] + 'Timesheet.pkl')
        d.to_pickle(dr['EXT'] +
                    dt.datetime.now().strftime('Timesheet-%y%m%d-%H%M%S.pkl'))
        display(d.tail())


    @out_1.capture(clear_output=True, wait=True)
    def start_click_1(b):
        '''
        Function for automatic time logging
        '''
        if b_start[1].icon == 'play':
            From[1].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[1].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[1].description = 'Elapsed Time'
            b_start[1].icon = 'stop'
            b_start[1].button_style = 'danger'
            display(read(dr['MAT'] + 'Timesheet.pkl').tail())
            threading.Thread(target=loop_1).start()

        else:
            To[1].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[1].description = 'To'
            b_start[1].icon = 'play'
            b_start[1].button_style = 'success'

            fnn = dr['MAT'] + 'Timesheet.pkl'

            if os.path.exists(fnn):
                d = read(fnn)
            else:
                d = pd.DataFrame(
                    columns=['Activity', 'From', 'To', 'Notes', 'Duration'])
            F = pd.to_datetime(From[1].value)
            T = pd.to_datetime(To[1].value)
            aa = make_df([[Act[1].value, F, T, Notes[1].value]])
            d = pd.concat((d, aa), ignore_index=True)

            d.to_pickle(fnn)
            d.to_pickle(dr['EXT'] +
                        dt.datetime.now().strftime('Timesheet-%y%m%d-%H%M%S.pkl'))

            display(d.tail())


    @out_1.capture(clear_output=True, wait=True)
    def start_click_2(b):
        '''
        Function for automatic time logging
        '''
        if b_start[2].icon == 'play':
            From[2].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[2].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[2].description = 'Elapsed Time'
            b_start[2].icon = 'stop'
            b_start[2].button_style = 'danger'
            threading.Thread(target=loop_2).start()
            display(read(dr['MAT'] + 'Timesheet.pkl').tail())

        else:
            To[2].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[2].description = 'To'
            b_start[2].icon = 'play'
            b_start[2].button_style = 'success'

            fnn = dr['MAT'] + 'Timesheet.pkl'

            if os.path.exists(fnn):
                d = read(fnn)
            else:
                d = pd.DataFrame(
                    columns=['Activity', 'From', 'To', 'Notes', 'Duration'])
            F = pd.to_datetime(From[2].value)
            T = pd.to_datetime(To[2].value)
            aa = make_df([[Act[2].value, F, T, Notes[2].value]])
            d = pd.concat((d, aa), ignore_index=True)

            d.to_pickle(fnn)
            d.to_pickle(dr['EXT'] +
                        dt.datetime.now().strftime('Timesheet-%y%m%d-%H%M%S.pkl'))

            display(d.tail())


    @out_1.capture(clear_output=True, wait=True)
    def start_click_3(b):
        '''
        Function for automatic time logging
        '''
        if b_start[3].icon == 'play':
            From[3].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[3].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[3].description = 'Elapsed Time'
            b_start[3].icon = 'stop'
            b_start[3].button_style = 'danger'
            threading.Thread(target=loop_3).start()
            display(read(dr['MAT'] + 'Timesheet.pkl').tail())

        else:
            To[3].value = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            To[3].description = 'To'
            b_start[3].icon = 'play'
            b_start[3].button_style = 'success'

            fnn = dr['MAT'] + 'Timesheet.pkl'

            if os.path.exists(fnn):
                d = read(fnn)
            else:
                d = pd.DataFrame(
                    columns=['Activity', 'From', 'To', 'Notes', 'Duration'])
            F = pd.to_datetime(From[3].value)
            T = pd.to_datetime(To[3].value)
            aa = make_df([[Act[3].value, F, T, Notes[3].value]])
            d = pd.concat((d, aa), ignore_index=True)

            d.to_pickle(fnn)
            d.to_pickle(dr['EXT'] +
                        dt.datetime.now().strftime('Timesheet-%y%m%d-%H%M%S.pkl'))

            display(d.tail())


    @out_2.capture(clear_output=True, wait=True)
    def edit_data_click(b):
        index = IND.value
        col = COL.value
        value = VAL.value
        d = read(dr['MAT'] + 'Timesheet.pkl')
        print('Old Value : %s      New Value : %s' % (d.loc[index, col], value))
        if col == 'Activity':
            if value in Activity:
                d.loc[index, col] = value
            else:
                print(
                    '%s is not in any activity. Please include %s in activity list first'
                    % (value, value))
        elif col in ['From', 'To']:
            value = pd.to_datetime(value)
            d.loc[index, col] = value
        else:
            d.loc[index, col] = value

        d['Duration'] = d['To'] - d['From']
        d.to_pickle(dr['MAT'] + 'Timesheet.pkl')
        d.to_pickle(dr['EXT'] +
                    dt.datetime.now().strftime('Timesheet-%y%m%d-%H%M%S.pkl'))
        print('Here is the new data')
        display(d.loc[index - 2:index + 2])

    @out_2.capture(clear_output=True, wait=True)
    def delete_entry(b):
        idx = IND.value
        d = read(dr['MAT']+'Timesheet.pkl')
        d1=d.drop(idx)
        d1=d1.reset_index(drop=True)
        d1.to_pickle(dr['MAT']+'Timesheet.pkl')
        display(read(dr['MAT']+'Timesheet.pkl').loc[idx-2:idx+2])


    @out_3.capture(clear_output=True, wait=True)
    def stop_click1(b):
        A = Act[4].value
        From_str = From[4].value
        To_str = To[4].value
        N = Notes[4].value
        idx = IND1.value

        F = pd.to_datetime(From_str)
        T = pd.to_datetime(To_str)

        val = make_df_id([[A, F, T, N]], idx)
        d = read(dr['MAT'] + 'Timesheet.pkl')
        d = d.append(val, ignore_index=False)
        d = d.sort_index().reset_index(drop=True)
        d.to_pickle(dr['MAT'] + 'Timesheet.pkl')
        d.to_pickle(dr['EXT'] +
                    dt.datetime.now().strftime('Timesheet-%y%m%d-%H%M%S.pkl'))
        display(d.loc[idx - 2:idx + 2])


    def ana_ui():
        out_0 = widgets.Output()
        out_1 = widgets.Output()
        out_2 = widgets.Output()
        out_3 = widgets.Output()

        def filter_data(k,date):
            date=dt.datetime(date.year,date.month,date.day)
            c1=(d['From']>pd.to_datetime(date))*(d['To']<=pd.to_datetime(date)+pd.to_timedelta('23:59:59'))

            c11=d[c1]
            idx=[i for i in d.index if d['To'][i].day==d['From'][i].day+1]
            c12=d.loc[idx]
            c10=c12[(c12['To']>=date)*(c12['To']<=date+pd.to_timedelta('23:59:59'))]
            c13=pd.concat((c10,c11))

            c2=c13[c13['Activity']==k]

            return c2

        def update_mat(k,mat,tot,date):
            c11=filter_data(k,date)
            tot[date]=c11['Duration'].sum()

            mat[date]=np.zeros(1440)
            ix=[int(np.round(i.total_seconds()/60)) for i in (c11['From']-date)]
            iy=[int(np.round(i.total_seconds()/60)) for i in (c11['To']-date)]
            for i,j in zip(ix,iy):
                if i<0:
                    mat[date][0:j]=1
                    date1=date-dt.timedelta(1)
                    date1=dt.datetime(date1.year,date1.month,date1.day)
                    if date1 >= dt.datetime(date_from.value.year,date_from.value.month,date_from.value.day):
                        ii=i+1440
                        mat[date1][ii:]=1
                else:
                    mat[date][i:j]=1


        def gen_mat(k,from_date,to_date):
            dates = pd.date_range(from_date,to_date)
            mat={}
            tot={}
            for date in dates:
                date=dt.datetime(date.year,date.month,date.day)
                update_mat(k,mat,tot,date)

            return mat,tot

        def plot_ts(k,tot):
            nmin={i.strftime('%a, %d %b'):tot[i].total_seconds()/60. for i in tot}

            a1=pd.Series(tot)
            a33 = pd.Series(nmin)
            a33 = a33.fillna(0)
            v=[str(tot[i])[7:] for i in tot]

            try:

                title = '%s\nMean = %s\n Regularity = %4.1f %% \n Maximum = %s on %s\n Minimum = %s on %s ' % (
                                k, str(a1.mean())[7:15], 100 * len(a33[a33 > 0]) / len(a33),
                                str(a1[a1 > dt.timedelta(0)].max())[7:15], a33[a33 > 0].argmax(),
                                str(a1[a1 > dt.timedelta(0)].min())[7:15], a33[a33 > 0].argmin())

            except ValueError:
                title = 'No \n %s \n Activitiy ' %(k)

            fig, ax = plt.subplots(figsize=(16, 8))
            plt.subplots_adjust(top=0.8, bottom=0.25)
            a33.plot.bar(width=1, ax=ax, color='g')
            ax.set_ylabel('Minutes', fontweight='bold')

            for j, i in enumerate(ax.patches):
                            if v[j] != '00:00:00':
                                if a33[j] < 0.2 * a33[a33 > 0].max():
                                    ax.text(i.get_x() + 0.45,
                                            1.5 * a33[j],
                                            v[j],
                                            fontsize=10,
                                            color='blue',
                                            rotation=90)
                                else:
                                    ax.text(i.get_x() + 0.45,
                                            0.1 * a33[j],
                                            v[j],
                                            fontsize=10,
                                            color='yellow',
                                            rotation=90)

            fig.suptitle(title, fontsize=18, fontweight='bold')
            fig.savefig(dr['FIG']+'ts.jpg',dpi=72)
            plt.close()
            return dr['FIG']+'ts.jpg'

        def plot_matrix(mat):
            dd1=np.zeros((len(mat),1440))
            for i,j in enumerate(mat):
                dd1[i,:]=mat[j]

            freq=100*(len(np.where(dd1.sum(axis=1)>0)[0])/dd1.shape[0])
            fig,ax=plt.subplots(figsize=(15,6))
            ax.imshow(dd1,aspect='auto',cmap=mpl.colors.ListedColormap(['white','g']))
            labels=[j.strftime('%a %d %b') for j in mat]
            plt.yticks(range(len(mat)),labels);
            xticks=np.arange(60,1440,60)
            xticklabels=np.arange(1,24)
            ax.set_xlabel('Time(hours)',fontweight='bold')
            ax.set_ylabel('Day',fontweight='bold')
            plt.xticks(xticks,xticklabels);
            ax.grid(color='y')
            ax.grid('off')
            fig.suptitle('Time Matrix of %s\nDaily frequency(Percent) = %4.1f' %(act_w.value,freq),fontsize=21,fontweight='bold')
            fig.savefig(dr['FIG']+'matrix.jpg',dpi=72)
            plt.close()
            return dr['FIG']+'matrix.jpg'

        @out_3.capture(clear_output=True, wait=True)
        def plot_act(b):
            d = read(dr['MAT']+'Timesheet.pkl')
            mat,tot=gen_mat(act_w.value,date_from.value,date_to.value)
            display(Image(plot_matrix(mat)))
            display(Image(plot_ts(act_w.value,tot)))

        d = read(dr['MAT']+'Timesheet.pkl')
        acts=set(d['Activity'])
        random_act = np.random.choice(list(acts), 1, replace=False)
        act_w=widgets.Dropdown(options=acts,
                                          value=random_act,
                                          description='Activity',
                                          disabled=False,
                                          )

        date_from = widgets.DatePicker(description='From',
                                       value=dt.date.today()-dt.timedelta(21),
                                       disabled=False)

        date_to = widgets.DatePicker(description='Upto',
                                     value=dt.date.today(),
                                     disabled=False)



        b_mat = widgets.Button(description='Show Matrix',
                       icon='play',
                       button_style='warning',
                       )

        b_mat.on_click(plot_act)

        matrix_ui=VBox([HBox([act_w,date_from,date_to,b_mat]),out_3])

        return matrix_ui

    def history_ui():
        date_wid = widgets.DatePicker(description='Pick a Date',
                                     value=dt.datetime.today(),
                                     disabled=False)




        def filter_data(date):
            d = read(dr['MAT']+'Timesheet.pkl')
            date=dt.datetime(date.year,date.month,date.day)
            c1=(d['From']>date)*(d['To']<=date+pd.to_timedelta('23:59:59'))
            c11=d[c1]

            idx=[i for i in d.index if d['To'][i].day==d['From'][i].day+1]
            c12=d.loc[idx]
            c10=c12[(c12['To']>=date)*(c12['To']<=date+pd.to_timedelta('23:59:59'))]

            for j in ['From','To']:
                c11[j]=[c11[j].iloc[i].strftime('%H:%M:%S') for i in range(len(c11[j]))]

            c13=pd.concat((c10,c11))
            display(c13)

        def total_df(date):
            d = read(dr['MAT']+'Timesheet.pkl')
            date=dt.datetime(date.year,date.month,date.day)
            c1=(d['From']>pd.to_datetime(date))*(d['To']<=pd.to_datetime(date)+pd.to_timedelta('23:59:59'))
            c11=d[c1]

            idx=[i for i in d.index if d['To'][i].day==d['From'][i].day+1]
            c12=d.loc[idx]
            c10=c12[(c12['To']>=date)*(c12['To']<=date+pd.to_timedelta('23:59:59'))]
            c13=pd.concat((c10,c11))

            acts=sorted(list(set(c13['Activity'])))

            act1=pd.Series(acts)
            tot=[c13[c13['Activity']==j]['Duration'].sum() for j in act1]
            tot1=pd.Series(tot)
            tot2=pd.DataFrame({'Activity': act1,'Total Duration':tot1})
            tot2 = tot2.sort_values(by='Total Duration',ascending=False)
            tot2 = tot2.reset_index(drop=True)
            display(tot2)



        out1 = widgets.interactive_output(filter_data, {'date': date_wid})
        out2 = widgets.interactive_output(total_df, {'date': date_wid})

        ui = VBox([date_wid,HBox([out1,out2])])

        return ui

    Act = {}
    From = {}
    To = {}
    Notes = {}
    Duration = {}

    random_act = np.random.choice(Activity, 5, replace=False)
    for i in range(5):

        Act[i] = widgets.Dropdown(options=Activity,
                                  value=random_act[i],
                                  description='Activity',
                                  disabled=False,
                                  layout=Layout(width='200px'))

        From[i] = widgets.Text(value='%s' %
                               (dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
                               placeholder='Start time',
                               description='From',
                               disabled=False,
                               layout=Layout(width='230px'))

        To[i] = widgets.Text(value='%s' %
                             (dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
                             placeholder='Start time',
                             description='To',
                             disabled=False,
                             layout=Layout(width='230px'))

        Notes[i] = widgets.Text(value='',
                                placeholder='Type something',
                                description='Notes',
                                disabled=False,
                                layout=Layout(width='220px'))

    b_stop = Button(description='',
                    icon='play',
                    button_style='info',
                    layout=Layout(width='100px'))

    b_stop1 = Button(description='',
                     icon='play',
                     button_style='info',
                     layout=Layout(width='100px'))

    b_stop.on_click(stop_click)

    b_stop1.on_click(stop_click1)

    add_row_ui = VBox([
        HBox([Act[0], From[0], To[0], Notes[0], b_stop],
             layout=Layout(margin='00000')), out_0
    ])

    b_start = {}
    timer_ui = {}

    for i in range(1, 4):
        b_start[i] = Button(description='',
                            icon='play',
                            button_style='success',
                            layout=Layout(width='100px'))

        timer_ui[i] = HBox([Act[i], b_start[i], From[i], To[i], Notes[i]],
                           layout=Layout(margin='00000'))

    b_start[1].on_click(start_click_1)
    b_start[2].on_click(start_click_2)
    b_start[3].on_click(start_click_3)

    COL = widgets.Dropdown(options=['Activity', 'From', 'To', 'Notes'],
                           value='Activity',
                           description='Columns',
                           disabled=False,
                           layout=Layout(width='200px'))

    app1 = VBox([timer_ui[1], timer_ui[2], timer_ui[3], out_1])


    if os.path.exists(dr['MAT'] + 'Timesheet.pkl'):

        sync_update()

        IND = widgets.Dropdown(options=read(dr['MAT'] + 'Timesheet.pkl').index[:],
                               value=read(dr['MAT'] + 'Timesheet.pkl').index[-1],
                               description='Index',
                               disabled=False,
                               layout=Layout(width='200px'))

        IND1 = widgets.Dropdown(options=read(dr['MAT'] + 'Timesheet.pkl').index[:],
                                value=read(dr['MAT'] + 'Timesheet.pkl').index[-1],
                                description='Index',
                                disabled=False,
                                layout=Layout(width='200px'))

        VAL = widgets.Text(value='',
                           placeholder='Type something',
                           description='Value',
                           disabled=False,
                           layout=Layout(width='300px'))

        b_edit = Button(description='Edit',
                        icon='play',
                        button_style='warning',
                        layout=Layout(width='100px'))

        b_del = Button(description='DELETE',
                        icon='play',
                        button_style='Danger',
                        layout=Layout(width='150px'))

        b_update=Button(description='Refresh',
                        icon='play',
                        button_style='warning',
                        layout=Layout(width='150px'))

        b_update.on_click(sync_update1)

        b_edit.on_click(edit_data_click)
        b_del.on_click(delete_entry)

        update_ui=VBox([b_update,out_5])

        edit_row_ui = VBox(
            [HBox([IND, COL, VAL, b_edit, b_del], layout=Layout(margin='00000')), out_2])

        insert_row_ui = VBox([
            HBox([IND1, Act[4], b_stop1]),
            HBox([From[4], To[4], Notes[4]]), out_3
        ])


        analysis_ui=ana_ui()
        hist=history_ui()
        tab = widgets.Tab()
        tab.children = [update_ui, add_row_ui, edit_row_ui, insert_row_ui, app1, analysis_ui,hist]
        tab.set_title(0, 'Updated Timesheet')
        tab.set_title(1, 'Manual Entry')
        tab.set_title(2, 'Edit Entry')
        tab.set_title(3, 'Insert Row')
        tab.set_title(4, 'Timer')
        tab.set_title(5, 'Analysis')
        tab.set_title(6, 'History')
        tab.box_style = 'danger'

    else:
        
        print(msg)
        tab = widgets.Tab()
        tab.children = [add_row_ui]
        tab.set_title(0, 'Manual Entry')

    return tab

# module level doc-string
__version__= '0.0.3'

__doc__ = """
jupyter-timetracker - a powerful time logging and analysis library for Python using Jupyter
=====================================================================

The goal of this library to easily track your time spent in various activities and get to know more about yourself in a way that which activities you do most in a day. Also it can keep track of your daily activities for years, decades or so long. If you are too obsessive about utilising every single second of your life, it can keep track of each second of your life. Also, if you are lazy and want to track only 2-3 important activities, then you can do that also by entering those activities that matters to you.

Main Features
-------------

Here are just a few of the things that timelog does vey well :

  - Ease of use : To use this library, you need not require knowledge of any programming language. Think of it as a      software where you just have to click on a few buttons and your work is done. The user interface is very simple, easy to use and self explanatory.
  
  - Can record your all activities involving time, you don't have to worry about having a handwritten timesheet, habit tracker etc. Use this library in your own creative ways.
  
  - Provison of Manual Entry :If you forget to track your activity in real time, but your remember some activities of the past then you can also manuall eneter all of your past activities.
  
  - Modifying past data : You can always edit/insert/delete any of your time entries in the past
  
  - Powerful Analysis : You can analyse how you spent your time for a particular duration on a bar chart as well as in a time matrix form let you know that on which hours of day you do that activity.
  
  - Know your History : After months of time logging, you can always look at a particular date in the past and view all the time entries of it along with the totla duration of your each activity.
  
  - Supports atimelogger csv reports : If you have used atimelogger app in mobile for time tracking, you can import all of your atimelogger data in csv format in this app. 
  
  - Synchronise to external drive : You can also synchronise your data from your external hard drive or pen drive.  
  
  - Backup: To prevent data loss from external deletion or accidently replacing file, it will keep a back of your data by default on each of your time entry by a different name containing timestamp. You can later manually delete those backups if size become too high
  
In short, You will get a clear picture of how you spend your time in a day, in a week, in a month or in a year. If you want to write an autobiography or memoir in the future , this python library can be of immense help.


Timesheet
-----------

Timesheet is basically the main database which has all records of your entered activities. It has 5 colums, Activity Name, From ( start time ), To ( Stop Time), Notes ( optional), Duration. Duration will automatically be calculated based on your start and stop time. You need only to select your activity from the drop down Menu and enter your start and stop time. Optionally, you can add your remarks/comments in the form of notes.

If you are working on your desktop, then you don't need to enter even start and stop time, you can go in *timer* tab, select an activity and click on green icon. It will take start time from your system's clock. When you finished your activity just click on red icon to stop as you can see in the above timesheet.

"""
