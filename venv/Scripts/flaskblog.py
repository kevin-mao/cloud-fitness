from flask import Flask, render_template
app=Flask(__name__)

posts=[

    {
        'author':'Dray',
        'title':'Blog Post 1',
        'content': 'Netflix and chill',
        'date_posted':'April 20. 2018'
    },

{
        'author':'Elon',
        'title':'Falcon Heavy',
        'content': 'ayy lmao',
        'date_posted':'April 21. 2018'
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', post=posts)

@app.route("/about")
def about():
    return "<h1> About Page</h1>"


if __name__== "__main__":
    app.run(debug=True)
