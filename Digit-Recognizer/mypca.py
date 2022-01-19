import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import matplotlib
from plotly.offline import init_notebook_mode, iplot
from plotly import tools
from myplot import *
from plotly.subplots import make_subplots

def my_scree(pca):
    scree = pca.explained_variance_ratio_*100
    
    fig = go.Figure(data=[
        go.Bar(name='Barre', x=np.arange(len(scree))+1, y=scree,text=np.around(scree,2),hoverinfo='x+y',textposition = 'auto'),
        go.Scatter(name='Pourcentages cumulés', x=np.arange(len(scree))+1, y=scree.cumsum())
    ])
    
    fig.update_layout(title="Eboulis des valeurs propres",
                  xaxis_title="rang de l'axe d'inertie",
                  yaxis_title="pourcentage d'inertie",
                  width = 700
                 )
    fig.show()



def my_pca(pcs, n_comp, pca, labels,X_projected,clusters,names, lims=None, colorsIdx=None,draw_circle=True,draw_proj=True,legend_width=200):
    d1 = 0
    d2 = 1
    
    if draw_circle == False and draw_proj == False:
        return
    
    if draw_circle == False or draw_proj == False:
        nb_col = 1
    else:
        nb_col = 2
    
    rows = int(n_comp / 2)
    
    titles = tuple()
    for i in range(0,rows):
        if draw_circle == True :
            titles = titles + ('Cercles des corrélations (F' + str(1+(2*i)) + ' et F' + str(2+(2*i)) + ')',)
        if draw_proj == True :
            titles = titles + ('Projection des individus (F' + str(1+(2*i)) + ' et F' + str(2+(2*i)) + ')',)
    
    figures = make_subplots(rows=rows, cols=nb_col,subplot_titles=titles,vertical_spacing = 0.1)
    
    shapes = []
    
    while d2 < n_comp:
        row = int((d2+1)/2)
        
        if row==1:
            showlegend=True
        else:
            showlegend=False
        
        if draw_circle == True :
            #Cercles de corrélations

            #Création des points
            points = go.Scatter(x=pcs[d1,:],
                                y=pcs[d2,:],
                                mode='markers+text',
                                marker=dict(size=4),
                                textposition= "top center",
                                text=labels,
                                name='Attributs',
                                legendgroup='circle',
                                showlegend=showlegend
                               )

            
            col = 1

            figures.add_trace(points,row=row,col=col)
            figures.update_xaxes(title_text='F{} ({}%)'.format(d1+1, round(100*pca.explained_variance_ratio_[d1],1)),
                                 row=row,
                                 col=col

                                )
            figures.update_yaxes(title_text='F{} ({}%)'.format(d2+1, round(100*pca.explained_variance_ratio_[d2],1)), row=row, col=col)

            xref = 'x' + str(col + nb_col * (row - 1))
            yref = 'y' + str(col + nb_col * (row - 1))

            #gestions des formes
            #Ajout du cercle
            shapes.append({'type':"circle",
                           'x0':-1,
                           'y0':-1,
                           'x1':1,
                           'y1':1,
                           'line_color':"black",
                           'xref':xref,
                           'yref':yref
                          }
                         )

            #Ajout des vecteurs
            for i in range(0,pcs.shape[1]):
                shapes.append({'type':"line",
                               'x0':0,
                               'y0':0,
                               'x1':pcs[d1][i],
                               'y1':pcs[d2][i],
                               'line':dict(
                                   color="LightSeaGreen",
                                   width=1
                               ),
                               'xref':xref,
                               'yref':yref
                              }
                             )


        if draw_proj == True :
            #Projection des individus
            col = nb_col

            #Gestion des couleurs par cluster
            unique_clusters = np.unique(clusters)

            if colorsIdx == None :
                colors_tab = get_color_list('rainbow', len(unique_clusters))
                colorsIdx = {}
                colorNb = 0
                for cluster_nb in unique_clusters:
                    colorsIdx[cluster_nb] = colors_tab[colorNb]
                    colorNb = colorNb + 1 

            df_scatter = pd.DataFrame()
            df_scatter['x'] = X_projected[:, d1]
            df_scatter['y'] = X_projected[:, d2]
            df_scatter['cluster'] = clusters
            df_scatter['colors'] = df_scatter['cluster'].map(colorsIdx) 

            #Création des points
            points = go.Scatter(x=df_scatter['x'],
                                y=df_scatter['y'],
                                mode='markers',
                                marker=dict(size=8,color=df_scatter['colors']),
                                text=names,
                                name='Individus',
                                legendgroup='proj',
                                showlegend=showlegend
                               )
            figures.add_trace(points,row=row,col=col)
            figures.update_xaxes(title_text='F{} ({}%)'.format(d1+1, round(100*pca.explained_variance_ratio_[d1],1)),
                                 row=row,
                                 col=2

                                )
            figures.update_yaxes(title_text='F{} ({}%)'.format(d2+1, round(100*pca.explained_variance_ratio_[d2],1)), row=row, col=2)

            #Gestion des centroïdes
            for cluster_nb in unique_clusters:
                df_scatter_clust = df_scatter[df_scatter['cluster']==cluster_nb].copy()
                centroid_len = len(df_scatter_clust['cluster'])
                centroid_x = sum(df_scatter_clust['x'])/centroid_len
                centroid_y = sum(df_scatter_clust['y'])/centroid_len

                centroid = go.Scatter(x=[centroid_x],
                                      y=[centroid_y],
                                      mode='markers',
                                      marker=dict(line_width=2,symbol="cross-dot",size=10,color=colorsIdx[cluster_nb]),
                                      text='Centroïde cluster ' + str(cluster_nb),
                                      name='Centroïde cluster ' + str(cluster_nb),
                                      legendgroup='centroid',
                                      showlegend=showlegend
                                     )
                figures.add_trace(centroid,row=row,col=col)


        
        d1 += 2
        d2 += 2
        
    if draw_circle == False or draw_proj == False:
        width=(800 + legend_width)
        height=int(800*(n_comp/2))
        
    else:
        width=(500 * nb_col + legend_width)
        height=int(500*(n_comp/2))
        
    """width=(400 * nb_col + legend_width)
    height=int(500*(n_comp/2))"""
        

    figures.update_layout(width=width,
                          height=height,
                          title_text="Visualisation ACP des " + str(n_comp) + " premières composantes",
                          showlegend=True,
                          shapes=shapes
                          
                         )
    figures.show()
        