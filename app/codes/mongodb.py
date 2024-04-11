
middle_points_aggregate = [
    {'$match': {
        # 'year': 2023,
        'middlePoint': {'$exists': False}
        }
    },
    # {'$limit': 10},
    {'$unwind': '$geometry.coordinates'},
    {'$group': {
        '_id': '$_id',
        'midLat': {'$avg': {'$arrayElemAt': ['$geometry.coordinates', 0]}},
        'midLon': {'$avg': {'$arrayElemAt': ['$geometry.coordinates', 1]}}
        }
    },
    {'$project': {
        'middlePoint': {
            'type': 'Point',
            'coordinates': [
                {'$round': ['$midLat', 7]},
                {'$round': ['$midLon', 7]}
                ]
            }
        }
    }
]

points_inside = {
    'year': 2023,
    'middlePoint': {
        '$geoWithin': {
            '$geometry': {
                'type': 'Polygon',
                'coordinates': '<city_bounds>'
            }
        }
    }
}