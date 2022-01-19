#------------------------------ IMPORTS -----------------------------------

import base64
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import os
import numpy as np
import cv2

#------------------------------- BACKEND ----------------------------------

from deepface import DeepFace
from operator import itemgetter

data = dict()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR,"images")


def add_to_dict(dict,key,value):
    #dict is a dict
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = [value]
    return 

def ask_database(img_path):
    results = list()
    for label in data:
        for path in data[label]:
            try :
                verify = DeepFace.verify(img_path,path,model_name="VGG-Face")
                if verify['verified'] == True:
                    result = (verify['verified'],verify['distance'],label)
                    results.append(result)
            except : continue
    results.sort(key=itemgetter(1))
    return results

for root,dirs,files in os.walk(image_dir):
    for file in files:
        if file.endswith("png") or file.endswith("jpeg") or file.endswith("jpg"):
            path = os.path.join(root,file)
            label = os.path.basename(os.path.dirname(path))
            add_to_dict(data,label,path)

#--------------------------- FRONTEND ------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-image-upload'),
])

#--------------------------- CALLBACKS -----------------------------------

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    jpg_as_np = np.frombuffer(decoded, dtype=np.uint8)
    image = cv2.imdecode(jpg_as_np, flags=1)
    cv2.imwrite('temp.png', image)

    image_filename = 'temp.png'
    try :
        name  = (ask_database(image_filename)[0][2],ask_database(image_filename)[0][1])
    except : 
        name = "Not found in Database"
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())

    return html.Div([
                html.Ul(id='my-list', children=[html.Li(i) for i in name]),
                html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode())),
    ])


@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

#-------------------------------- LAUNCHER----------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)