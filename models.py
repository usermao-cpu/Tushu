"""
数据库模型 - Book 模型
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    """图书模型"""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='书名')
    author = db.Column(db.String(100), nullable=False, comment='作者')
    isbn = db.Column(db.String(20), unique=True, comment='ISBN编号')
    publisher = db.Column(db.String(100), comment='出版社')
    year = db.Column(db.Integer, comment='出版年份')
    description = db.Column(db.Text, comment='图书简介')

    def __repr__(self):
        return f'<Book {self.title}>'
