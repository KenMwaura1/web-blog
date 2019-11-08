import datetime
import uuid

from src.common.database import Database


class Post(object):
    def __init__(self, blog_id, title, content, author, created_date=datetime.datetime.utcnow(), _id=None):
        self.created_date = created_date
        self.blog_id = blog_id
        self.title = title
        self.content = content
        self.author = author
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='posts',
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'blog_id': self.blog_id,
            'author': self.author,
            'title': self.title,
            'content': self.content,
            'created_date': self.created_date
        }

    # Used to retrieve a post after an id is passed
    @classmethod
    def from_mongo(cls, id):
        post_data = Database.find_one(collection='posts', query={'_id': id})
        return cls(**post_data)

    @staticmethod
    def from_blog(id):
        return [post for post in Database.find(collection='posts', query={'blog_id': id})]

    @staticmethod
    def del_post(id):
        del_post = Database.delete_one(collection='posts', query={'_id': id})
        return str(del_post.raw_result)

    def update_post(self, id):
        Database.update(collection='posts', query={'_id': id}, data=self.json())
