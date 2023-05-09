import json


class CoffeeDto:
    def __init__(self, id, url, image_url, source, title, price, description, roast, tastes, recommended_brew_methods,
                 sort, category, country, processing_method, variety, score):
        self.id = id
        self.url = url
        self.image_url = image_url
        self.source = source
        self.title = title
        self.price = price
        self.description = description
        self.roast = roast
        self.tastes = tastes
        self.recommended_brew_methods = recommended_brew_methods
        self.sort = sort
        self.category = category
        self.country = country
        self.processing_method = processing_method
        self.variety = variety
        self.score = score

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'image_url': self.image_url,
            'source': self.source,
            'title': self.title,
            'price': self.price,
            'description': self.description,
            'roast': self.roast,
            'tastes': self.tastes,
            'recommended_brew_methods': self.recommended_brew_methods,
            'sort': self.sort,
            'category': self.category,
            'country': self.country,
            'processing_method': self.processing_method,
            'variety': self.variety,
            'score': self.score
        }

    @staticmethod
    def from_json(json_data):
        coffee_data = json.loads(json_data)
        return CoffeeDto(
            id=coffee_data['id'],
            url=coffee_data['url'],
            image_url=coffee_data['imageUrl'],
            source=coffee_data['source'],
            title=coffee_data['title'],
            price=coffee_data['price'],
            description=coffee_data['description'],
            roast=coffee_data['roast'],
            tastes=set(coffee_data['tastes']),
            recommended_brew_methods=set(coffee_data['recommendedBrewMethods']),
            sort=coffee_data['sort'],
            category=coffee_data['category'],
            country=coffee_data['country'],
            processing_method=coffee_data['processingMethod'],
            variety=coffee_data['variety'],
            score=coffee_data['score']
        )
