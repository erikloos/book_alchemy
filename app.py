from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from data_models import db, Author, Book
import os
import requests



app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/libary.sqlite')}"
db.init_app(app)

@app.route('/', methods = ['GET'])
def home():
    sort_by = request.args.get('sort')
    query = db.session.query(Book, Author) \
        .join(Author, Book.author_id == Author.id)

    if sort_by == "title":
        query = query.order_by(Book.title.asc())

    elif sort_by == "author":
        query = query.order_by(Author.name.asc())

    books = query.all()

    return render_template('home.html', books=books)



@app.route('/add_author', methods = ['GET', 'POST'])
def add_author():
    if request.method == 'GET':
        return render_template('add_author.html')

    else:
        author_name = request.form.get("name")
        author_birthdate = request.form.get("birthdate")
        author_date_of_death = request.form.get("date_of_death")
        try:
            author_birthdate = datetime.strptime(author_birthdate, "%Y-%m-%d").date()
            if not author_date_of_death:
                author_date_of_death = None
            else:
                author_date_of_death = datetime.strptime(author_date_of_death, "%Y-%m-%d").date()
            new_author = Author(
                name = author_name,
                birth_date = author_birthdate,
                date_of_death =  author_date_of_death
            )
            db.session.add(new_author)
            db.session.commit()
        except ValueError:
            return jsonify("Author could not added"), 400
        except Exception:
            db.session.rollback()
            return jsonify("Database error"), 500
        return jsonify("Author was added successfully."), 201


@app.route('/add_book', methods = ['GET', 'POST'])
def add_book():
    if request.method == 'GET':
        authors = db.session.query(Author).all()
        return render_template('add_book.html', authors=authors)
    else:
        new_title = request.form.get("title")
        new_isbn = request.form.get("ISBN").replace("-", "")
        new_publication_year = request.form.get("publication_year")
        new_author_id = request.form.get("authors")
        try:
            new_publication_year = int(new_publication_year)
            new_author_id = int(new_author_id)
            new_book = Book(
                title = new_title,
                isbn = new_isbn,
                publication_year = new_publication_year,
                author_id = new_author_id
            )
            db.session.add(new_book)
            db.session.commit()
        except ValueError:
            return jsonify("Book could not added"), 400
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            return jsonify(f"Database error: {str(e)}"), 500

        return jsonify("Book was added successfully."), 201


# Creat table in database
# with app.app_context():
#   db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)