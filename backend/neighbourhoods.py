import csv
import pandas as pd
import json
import folium


def render():

    areas_loc = {}
    all_area_names = []
    coordiantes = []
    # Change as required
    state_geo_path = "berlin.geojson"
    json_file = open(state_geo_path, 'r').read()
    areas = json.loads(json_file)
    json_length = 95
    index = 0

    for index in range(0, json_length):
        area = areas['features'][index]
        area_name = area.get('properties').get('name')
        cords = area.get('geometry').get('coordinates')
        all_area_names.append(area_name)
        coordiantes.append(cords)

    # This would just be an array of the column with the areas
    predictions = []
    with open('predicted_neighbourhoods.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                predictions.append(row)
    new_predictions = []
    for item in predictions:
        (_, _, name, lat, lon, pred) = item
        name = name.replace(".", "")
        if '-' in name:
            [name1, name2] = name.split('-')
            name1 = name1.replace(" ", "")
            name2 = name2.replace(" ", "")
            new_predictions.append([name1.title(), lat, lon, pred])
            new_predictions.append([name2.title(), lat, lon, pred])
        else:
            new_predictions.append([name.title(), lat, lon, pred])

    the_names = []
    the_colors = []

    print('areas')
    print(all_area_names)
    for (name, cord, cord2, pred) in new_predictions:
        print(pred)
        if name in all_area_names:
            print('here')
            the_names.append(name)
            if(pred == '0'):
                the_colors.append(0)
            elif(pred == '1'):
                the_colors.append(1)
        elif name is "Treptow":
            # use Alt-Treptow
            the_names.append('Alt-Treptow')
            if(pred == '0'):
                the_colors.append(0)
            elif(pred == '1'):
                the_colors.append(1)


    data = list(zip(the_names, the_colors))

    # print(data)
    map_dict = pd.DataFrame(data, columns=['Names', 'Colours'])

    print(map_dict.head())

    def get_color(feature):
        value = map_dict.get(feature.properties.Names)
        print(value)
        if value is None:
            return '#8c8c8c'  # MISSING -> gray
        else:
            return 'red'


    def style_function(a):
        return {
            'fillOpacity': 0.5,
            'weight': 0,
            'fillColor': '#black'
        }


    state_geo = "berlin.geojson"
    m = folium.Map(location=[52.534537, 13.402557], zoom_start=12)
    m.choropleth(state_geo,
                data=map_dict,
                columns=['Names', 'Colours'],
                key_on='feature.properties.name',
                fill_color='YlOrRd')

    m.save("../frontend/map.html")
    m
