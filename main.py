import os
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **kw):
        t = jinja_env.get_template(template)
        return t.render(kw)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class BlogPost(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class MainPage(Handler):
    def render_front(self, title="", body="", error=""):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC")

        self.render("front.html", title=title, body=body, error=error, blogposts=blogposts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = BlogPost(title=title, body=body)
            b.put() # stores post in database
            self.redirect("/")
        else:
            error = "We need a title and some text!"
            self.render_front(title, body, error)


class Blog(Handler):
    def render_blog(self):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("blog.html", blogposts=blogposts)

    def get(self):
        self.render_blog()


class NewPost(Handler):
    def render_new_post_form(self, title="", body="", error=""):
        #blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("new-post.html", title=title, body=body, error=error)

    def get(self):
        self.render_new_post_form()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = BlogPost(title=title, body=body)
            b.put() # stores post in database
            self.redirect("/blog")
        else:
            error = "We need a title and some text!"
            self.render_new_post_form(title, body, error)


class ViewPost(Handler):
     def get(self, id):
         id = int(id)
         blogpost = BlogPost.get_by_id(id)
         self.render("view-post.html", blogpost=blogpost, id=id)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)
