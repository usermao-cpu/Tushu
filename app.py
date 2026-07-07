"""
图书管理系统 - Library Management System
基于 Flask 的简单图书管理应用
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Book

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'library-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """首页 - 显示所有图书"""
    books = Book.query.order_by(Book.id.desc()).all()
    return render_template('index.html', books=books)


@app.route('/book/add', methods=['GET', 'POST'])
def add_book():
    """添加图书"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publisher = request.form.get('publisher', '').strip()
        year = request.form.get('year', type=int)
        description = request.form.get('description', '').strip()

        if not title or not author:
            flash('书名和作者为必填项', 'danger')
            return render_template('add_book.html')

        if isbn and Book.query.filter_by(isbn=isbn).first():
            flash('该 ISBN 已存在', 'danger')
            return render_template('add_book.html')

        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            publisher=publisher,
            year=year,
            description=description
        )
        db.session.add(book)
        db.session.commit()
        flash('图书添加成功!', 'success')
        return redirect(url_for('index'))

    return render_template('add_book.html')


@app.route('/book/<int:book_id>')
def view_book(book_id):
    """查看图书详情"""
    book = Book.query.get_or_404(book_id)
    return render_template('view_book.html', book=book)


@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    """编辑图书信息"""
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.isbn = request.form.get('isbn', '').strip()
        book.publisher = request.form.get('publisher', '').strip()
        book.year = request.form.get('year', type=int)
        book.description = request.form.get('description', '').strip()

        if not book.title or not book.author:
            flash('书名和作者为必填项', 'danger')
            return render_template('edit_book.html', book=book)

        db.session.commit()
        flash('图书信息已更新!', 'success')
        return redirect(url_for('view_book', book_id=book.id))

    return render_template('edit_book.html', book=book)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """删除图书"""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('图书已删除!', 'success')
    return redirect(url_for('index'))


@app.route('/search')
def search():
    """搜索图书"""
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('index'))

    books = Book.query.filter(
        db.or_(
            Book.title.ilike(f'%{q}%'),
            Book.author.ilike(f'%{q}%'),
            Book.isbn.ilike(f'%{q}%'),
            Book.publisher.ilike(f'%{q}%')
        )
    ).order_by(Book.id.desc()).all()

    return render_template('search.html', books=books, query=q)


# ----- REST API -----
@app.route('/api/books', methods=['GET'])
def api_get_books():
    """获取所有图书 (API)"""
    books = Book.query.order_by(Book.id.desc()).all()
    return jsonify([{
        'id': b.id,
        'title': b.title,
        'author': b.author,
        'isbn': b.isbn,
        'publisher': b.publisher,
        'year': b.year,
        'description': b.description
    } for b in books])


@app.route('/api/books', methods=['POST'])
def api_add_book():
    """添加图书 (API)"""
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({'error': '书名和作者为必填项'}), 400

    if data.get('isbn') and Book.query.filter_by(isbn=data['isbn']).first():
        return jsonify({'error': '该 ISBN 已存在'}), 400

    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data.get('isbn', ''),
        publisher=data.get('publisher', ''),
        year=data.get('year'),
        description=data.get('description', '')
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': '添加成功', 'id': book.id}), 201


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def api_delete_book(book_id):
    """删除图书 (API)"""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': '删除成功'})


@app.route('/health')
def health():
    """健康检查端点"""
    return jsonify({'status': 'healthy', 'service': 'library-management'}), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
