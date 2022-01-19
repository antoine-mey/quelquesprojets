import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import matplotlib
from plotly.offline import init_notebook_mode, iplot
from plotly import tools

def get_color_list(palette,nb):
    cmap = matplotlib.cm.get_cmap(palette)
    norm = matplotlib.colors.Normalize(vmin=0, vmax=255)
    rgb = []
    for i in range(0, 255):
        k = matplotlib.colors.colorConverter.to_rgb(cmap(norm(i)))
        rgb.append(k)
    
    if nb > 1:
        h = 1.0/(nb-1)
        color_list = []

        for k in range(nb):
            C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
            color_list.append('rgb'+str((C[0], C[1], C[2])))
    else:
        color_list = []
        C = list(map(np.uint8, np.array(cmap(1)[:3])*255))
        color_list.append('rgb'+str((C[0], C[1], C[2])))
        

    return color_list
	
def my_line(df,dict_plot,df_couleur=pd.DataFrame()):
    
    if df_couleur.empty == False :
        gest_couleur_custom = True
    else:
        gest_couleur_custom = False

    xaxis = dict_plot.get('xaxis')
    yaxis = dict_plot.get('yaxis')
    xaxis_dict = dict_plot.get('xaxis_dict',dict())
    yaxis_dict = dict_plot.get('yaxis_dict',dict())
    height = dict_plot.get('height',500)
    width = dict_plot.get('width',1000)
    mode = dict_plot.get('mode','lines') #'lines+markers', 'lines','markers'

    title = dict_plot.get('title',' ')
    grpby_clause = [xaxis]
    agg_funct = dict_plot.get('agg_funct','count')
    hue = dict_plot.get('hue')

    if hue == None :
        hue_fl = False
    elif isinstance(hue, str) and len(hue) > 0 :
        grpby_clause.append(hue)
        hue_fl = True
        hue_lst = [hue]
    elif isinstance(hue, list):
        grpby_clause.extend(hue)
        hue_fl = True
        hue_lst = hue

    #Gestion des couleurs
    if gest_couleur_custom :
        df_couleur_idx = df_couleur.set_index(hue_lst).copy()

    #on fait le groupby demandé
    df_grp = df.groupby(grpby_clause).agg({yaxis:agg_funct}).copy()
    df_grp = df_grp.reset_index()

    lines = []

    #On construit une liste d'éléments uniques si hue est à true
    if hue_fl == True:
        df_hue = pd.DataFrame(df_grp,columns=hue_lst).drop_duplicates()
        
        for row in df_hue.itertuples(index=False):
            df_grp_by_hue = df_grp.copy()
            hue_item_lst = []
            name = ''
            
            #On applique tous les filtres
            for hue_item in hue_lst: 
                df_grp_by_hue = df_grp_by_hue[df_grp_by_hue[hue_item] == getattr(row, hue_item)]
                hue_item_lst.append(getattr(row, hue_item))
                name = name + hue_item + ' : ' + getattr(row, hue_item) + '\n' 
            
            if gest_couleur_custom == True :
                hue_item_tuple = tuple(hue_item_lst)
                color = df_couleur_idx.loc[hue_item_tuple]['couleur']
                dict_line = dict(color = color,width = 1)
            else :
                dict_line = dict(width = 1) 
            
            x = df_grp_by_hue[xaxis]
            y = df_grp_by_hue[yaxis]
            
            line = go.Scatter(
                x=x, 
                y=y,
                name=name,
                text=name,
                hoverinfo='text+y',
                line = dict_line,
                mode=mode,
                marker_size=3
            )
            
            lines.append(line)
            
    else:
        x = df_grp[xaxis]
        y = df_grp[yaxis]
        
        line = go.Scatter(
            x=x,
            y=y,
            name=yaxis,
            text=yaxis,
            hoverinfo='y',
            line = dict(width = 1),
            mode=mode,
            marker_size=3
        )
        
        lines.append(line)
        


    layout = go.Layout(height = height,
                       width = width,
                       title = dict(text=title,xref="paper",x=0.5,y=0.95),
                       yaxis=yaxis_dict,
                       xaxis=xaxis_dict)


    fig  = go.Figure(data=lines, layout=layout)
    py.iplot(fig)
	
def my_bar(df,dict_plot,df_couleur=pd.DataFrame()):

    xaxis = dict_plot.get('xaxis')
    yaxis = dict_plot.get('yaxis')
    xaxis_dict = dict_plot.get('xaxis_dict',dict())
    yaxis_dict = dict_plot.get('yaxis_dict',dict())
    height = dict_plot.get('height',500)
    width = dict_plot.get('width',500)
    cmap = dict_plot.get('cmap')
    orientation = dict_plot.get('orientation','v') #'v' pour vertical, 'h' pour horizontal
    grpby = dict_plot.get('grpby',True)
    title = dict_plot.get('title',' ')
    grpby_clause = [xaxis]
    agg_funct = dict_plot.get('agg_funct','count')
    hue = dict_plot.get('hue')
    sort_x_by_y = dict_plot.get('sort_x_by_y',False)
    sort_x_by_y_order = dict_plot.get('sort_x_by_y_order','asc') 
    xround = dict_plot.get('xround')
    yround = dict_plot.get('yround')
    color_by_value = dict_plot.get('color_by_value',' ')
    hovertext_cols = dict_plot.get('hovertext_cols')
    text_col =dict_plot.get('text_col')
    textposition = dict_plot.get('textposition',"none")

    if hue == None :
        hue_fl = False
    elif isinstance(hue, str) and len(hue) > 0 :
        grpby_clause.append(hue)
        hue_fl = True
        hue_lst = [hue]
    elif isinstance(hue, list):
        grpby_clause.extend(hue)
        hue_fl = True
        hue_lst = hue
        
    if color_by_value != ' ' :
        grpby_clause.append(color_by_value)
        
    #Gestion des couleurs
    gest_couleur_cmap = False
    
    if df_couleur.empty == False :
        gest_couleur_custom = True
    else:
        gest_couleur_custom = False
        if cmap != None:
            gest_couleur_cmap = True

    if gest_couleur_custom :
        if color_by_value != ' ':
            df_couleur_idx = df_couleur.set_index(color_by_value).copy()
        elif hue_fl:
            df_couleur_idx = df_couleur.set_index(hue_lst).copy()
        else :
            df_couleur_idx = df_couleur.set_index(xaxis).copy()
            
    



    #on fait le groupby demandé
    if grpby == True:
        df_grp = df.groupby(grpby_clause).agg({yaxis:agg_funct}).copy()
        df_grp = df_grp.reset_index()
    else:
        df_grp = df.copy()
        
    if sort_x_by_y == True :
        if hue_fl == False : 
            xaxis_dict["categoryorder"] = 'array'
            if sort_x_by_y_order == 'asc' :
                xaxis_dict["categoryarray"] = [x for _, x in sorted(zip(df_grp[yaxis], df_grp[xaxis]))] 
            else :
                xaxis_dict["categoryarray"] = [x for _, x in sorted(zip(df_grp[yaxis], df_grp[xaxis]), reverse = True)]
            
        else :
            yaxis_dict["categoryorder"] = 'array'
            if sort_x_by_y_order == 'asc' :
                xaxis_dict["categoryarray"] = [x for _, _, x in sorted(zip(df_grp[hue], df_grp[yaxis], df_grp[xaxis]))] 
            else :
                xaxis_dict["categoryarray"] = [x for _, _, x in sorted(zip(df_grp[hue], df_grp[yaxis], df_grp[xaxis]), reverse = True)]
    

    #On swap les axes 
    if orientation == 'h':
        xaxis, yaxis = yaxis, xaxis
        xaxis_dict, yaxis_dict = yaxis_dict, xaxis_dict
        
    #Arrondis si demandés
    if xround != None :
        df_grp[xaxis] = df_grp[xaxis].round(decimals=xround) 
    if yround != None :
        df_grp[yaxis] = df_grp[yaxis].round(decimals=yround) 
  
    bars = []

    #On construit une liste d'éléments uniques si hue est à true
    if hue_fl == True:
        df_hue = pd.DataFrame(df_grp,columns=hue_lst).drop_duplicates()
        
        for row in df_hue.itertuples(index=False):
            df_grp_by_hue = df_grp.copy()
            hue_item_lst = []
            name = ''
            
            #On applique tous les filtres
            for hue_item in hue_lst: 
                df_grp_by_hue = df_grp_by_hue[df_grp_by_hue[hue_item] == getattr(row, hue_item)]
                hue_item_lst.append(getattr(row, hue_item))
                name = name + hue_item + ' : ' + str(getattr(row, hue_item)) + '\n' 
            
            if gest_couleur_custom == True :
                if color_by_value == ' ':
                    hue_item_tuple = tuple(hue_item_lst)
                    color = df_couleur_idx.loc[hue_item_tuple]['couleur']
                    dict_marker = dict(color = color)
                else :
                    colors = [df_couleur_idx.loc[x]['couleur'] for x in df_grp_by_hue[color_by_value]]
                    dict_marker = dict(color = colors)
                    
            else :
                if color_by_value == ' ' or gest_couleur_cmap==False:
                    dict_marker = dict()  
                else :
                    color_list = get_color_list(cmap, df_grp_by_hue[color_by_value].nunique(),True)
                    lst_values_for_col = list(df_grp_by_hue[color_by_value].unique())
                    colors = [color_list[lst_values_for_col.index(x)] for x in df_grp_by_hue[color_by_value]]
                    dict_marker = dict(color = colors)

            x = df_grp_by_hue[xaxis]
            y = df_grp_by_hue[yaxis]
            
            if hovertext_cols == None:
                hovertext = ''
            else:
                hovertext = ''
                for col in hovertext_cols :
                    hovertext += col + " : " + df_grp_by_hue[col].astype(str) + "<br>"
                    
            if text_col == None:
                if orientation == 'h':
                    text = x
                else :
                    text = y
            else:
                text = df_grp_by_hue[text_col]            
                
            
            bar = go.Bar(
                x=x, 
                y=y,
                name=name,
                text=text,
                hovertext = hovertext,
                textposition = textposition,
                hoverinfo='name+text+x',
                hoverlabel={'namelength' :-1},
                marker = dict_marker,
                orientation=orientation
            )
            
            bars.append(bar)
    else:
        x = df_grp[xaxis]
        y = df_grp[yaxis]
        
        if gest_couleur_custom == True :
            colors = []
            if color_by_value == ' ':
                for i in x: 
                    colors.append(df_couleur_idx.loc[i]['couleur'])
            else:
                colors = [df_couleur_idx.loc[x]['couleur'] for x in df_grp[color_by_value]]
                
            dict_marker = dict(color = colors) 
            
        elif gest_couleur_cmap :
            if color_by_value == ' ':
                colors = get_color_list(cmap, len(df_grp[xaxis]))
            else :
                color_list = get_color_list(cmap, df_grp[color_by_value].nunique())
                lst_values_for_col = list(df_grp[color_by_value].unique())
                colors = [color_list[lst_values_for_col.index(x)] for x in df_grp[color_by_value]]
            dict_marker = dict(color = colors) 
            
        else :
            dict_marker = dict() 
        
        if hovertext_cols == None:
            hovertext = ''
        else:
            hovertext = ''
            for col in hovertext_cols :
                hovertext += col + " : " + df_grp_by_hue[col].astype(str) + "<br>"

        if text_col == None:
            if orientation == 'h':
                text = x
            else :
                text = y
        else:
            text = df_grp_by_hue[text_col] 
        
        
        
        
        bar = go.Bar(
            x=x,
            y=y,
            name=xaxis,
            text=text,
            hoverinfo='x+y',
            hovertext = hovertext,
            textposition = 'auto',
            orientation=orientation,
            marker=dict_marker
        )
        
        bars.append(bar)
    
    
    layout = go.Layout(height = height,
                       width = width,
                       template='plotly_white',
                       title = dict(text=title,xref="paper",x=0.5,y=0.95),
                       yaxis=yaxis_dict,
                       xaxis=xaxis_dict)


    fig  = go.Figure(data=bars)
    fig.layout = layout
    #fig.show()
    
    py.iplot(fig)
		

