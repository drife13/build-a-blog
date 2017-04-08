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


def get_posts(limit, offset):
    blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT "
                            + str(limit) + " OFFSET " + str(offset))
    return blogposts


class MainHandler(Handler):
    def get(self):
        self.redirect("/blog")


class Blog(Handler):
    def render_blog(self, page):
        if page.isdigit() and int(page)>=1:
            page = int(page)
            blogposts = get_posts(5, (page-1)*5)

            next_page_count = blogposts.count(offset=page*5, limit=5)
            page_count = blogposts.count(offset=(page-1)*5, limit=5)

            if page_count==0:
                self.error(404)
            else:
                self.render("blog.html", blogposts=blogposts, page=page,
                                         next_page_count=next_page_count)
        else:
            self.error(404)

    def get(self):
        page = self.request.get("page","1") # default to 1
        self.render_blog(page)


class NewPost(Handler):
    def render_new_post_form(self, title="", body="", error=""):
        self.render("new-post.html", title=title, body=body, error=error)

    def get(self):
        self.render_new_post_form()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            b = BlogPost(title=title, body=body)
            b.put() # stores post in database
            post_route = "/blog/"+str(b.key().id())
            self.redirect(post_route)
        else:
            error = "We need a title and some text!"
            self.render_new_post_form(title, body, error)


class ViewPost(Handler):
     def get(self, id):
         id = int(id)
         blogpost = BlogPost.get_by_id(id)

         self.render("view-post.html", blogpost=blogpost, id=id)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)
