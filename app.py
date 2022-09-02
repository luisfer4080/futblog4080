from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from webforms import NameForm, TestForm, UserForm, UpdateUserForm, PostForm, LoginForm, TeamForm, PlayerForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
from datetime import datetime, date
import uuid as uuid
import os

# Create Flask instance

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = "xxslinxx_1"

UPLOAD_FOLDER ='static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create databse

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_DATABASE_URI'] =  'postgres://uofwekzwzufycb:57a25b8d20529b749e1b6a17dc5b639a3363a84a9f719b0e7d516d676168e23b@ec2-44-206-137-96.compute-1.amazonaws.com:5432/d58s6d3l4gth2n'



# Initilaize the database

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login manager

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create the models of the database

class User (db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))
    type = db.Column(db.Integer )
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    posts = db.relationship('Post', backref = 'user')
    teams = db.relationship('Team', backref = 'user')
    players = db.relationship('Player', backref = 'user')
    
    @property
    def password(self):
        raise AttributeError('password is not readeable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)

class Post (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True)
    content = db.Column(db.Text)
    slug = db.Column(db.String(150), unique=True)
    post_pic = db.Column(db.String(255))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    fk_user =  db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

team_player = db.Table('team_player',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id')),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'))
)

class Team (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    text = db.Column(db.Text, nullable = False)
    palmares = db.Column(db.Text, nullable = False)
    team_pic = db.Column(db.String(), nullable = False)
    type = db.Column(db.String(150), nullable = False)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    players = db.relationship('Player', secondary=team_player, backref='plays')
    fk_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    

class Player (db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    text = db.Column(db.Text, nullable = False)
    palmares = db.Column(db.Text, nullable = False)
    birth = db.Column(db.Date, nullable = False)
    age = db.Column(db.Integer, nullable = False)
    nationality = db.Column(db.Text, nullable = False)
    position = db.Column(db.String, nullable = False)
    player_pic = db.Column(db.String(), nullable = False)
    player_small_pic = db.Column(db.String(), nullable = False)
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    fk_user = db.Column(db.Integer, db.ForeignKey('user.id'))


# Start the creation of routes

@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.order_by(Post.date_created)
    teams = Team.query.order_by(Team.date_created)
    players = Player.query.order_by(Player.date_created)
    return render_template("index.html", posts=posts, teams=teams, players=players, user=current_user)

# User releated routes

@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    username = None
    email = None
    hashed_pw = None
    name= None
    form = UserForm()
    users = User.query.order_by(User.date_created)


    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")

        email_exist = User.query.filter_by(email=email).first()
        username_exist = User.query.filter_by(username=username).first()
        
        if email_exist is None and username_exist is None:
            
            users_2 = User.query.all()

            if users_2:
                type = 2
            else:
                type = 1

            new_user = User(email=email,username=username,type=type,password_hash=hashed_pw,name=name)
            db.session.add(new_user)
            db.session.commit() 

        elif email_exist is not None:
            flash("Email already exist", category="error")
        elif username_exist is not None:
            flash("Username already exist", category="error")

        form.name.data = ''
        form.username.data = ''
        form.password_hash.data = ''
        form.password_hash_2.data = ''
        form.email.data = ''

        flash("Username added successfully", category="success")

        return redirect(url_for('home'))


    return render_template("signup.html",user=current_user, username=username, email=email, name=name, password_hash=hashed_pw, form=form, users=users)

@app.route('/user/login', methods=['GET', 'POST'])
def login():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        form.email.data = ''
        form.password.data = ''

        user = User.query.filter_by(email=email).first()

        if user is not None:
            if check_password_hash(user.password_hash, password):
                login_user(user, remember = True)
                flash("Login successfull welcome to fut-blog", category="success")
                return redirect(url_for('home'))
            else:
                flash("Invalid password ", category="error")
                return render_template("login.html", form = form, user=current_user)
        else:
            flash("Email dont exist ", category="error")
            return render_template("login.html", form = form, user=current_user)

    else:
        return render_template("login.html", form = form, user=current_user)  


@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):

    form = UpdateUserForm()
    user_to_update = User.query.get_or_404(id)

    if id == current_user.id or current_user.id == 1:
        if request.method == "POST": 
            user_to_update.username = request.form['username']
            user_to_update.name = request.form['name']
            user_to_update.email = request.form['email']
            user_to_update.password_hash = request.form['password_hash']

            try:
                db.session.commit()
                flash("User updated successfully", category="success")
                return render_template("update_user.html", form=form, user_to_update=user_to_update)
            except:
                flash("Error!! ... looks that there was a problem", category="error")
                return render_template("update_user.html", form=form, user_to_update=user_to_update)
        else:
            return render_template("update_user.html", form=form, user_to_update=user_to_update, user=current_user)
    else:
        flash("Error!! ... you dont have access to this user", category="error")
        return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UpdateUserForm()
    id=current_user.id
    user_to_update = User.query.get_or_404(id)

    if request.method == "POST": 
        user_to_update.username = request.form['username']
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.password_hash = request.form['password_hash']

        try:
            db.session.commit()
            flash("User updated successfully", category="success")
            return render_template("dashboard.html", form=form, user=current_user)
        except:
            flash("Error!! ... looks that there was a problem", category="error")
            return render_template("dashboard.html", form=form, user=current_user)
    else:
        return render_template("dashboard.html", form=form, user=current_user)
   

@app.route('/admin')
@login_required
def admin():

    if current_user.id != 1:
        flash("You need admin acces to get in to this section", category="error")
        return redirect(url_for('home'))
    else:
        users = User.query.all()
        teams = Team.query.all()
        players = Player.query.all()
        posts = Post.query.all()
        return render_template("admin.html",user=current_user,users=users, teams=teams, players = players, posts = posts)



@app.route('/search')
@login_required
def search():

    page =request.args.get("page", default="none")
    type =request.args.get("type", default="none")
    id = request.args.get("id", default="none")
    
    if id != "none" :   
        user = User.query.filter_by(id=id).first()

    if page != "none" and type != "none":
        if page == "1":
            if type == "1":
                post_exist = Post.query.filter_by(author=user.id).all()
                team_exist = Team.query.filter_by(author=user.id).all()
                player_exist = Player.query.filter_by(author=user.id).all()
                return render_template("view_user_posts.html", user_2=user,user=current_user, posts=post_exist, teams=team_exist, players=player_exist)
            elif type == "2":
                post_exist = Post.query.filter_by(author=user.id).all()
                return render_template("view_user_posts.html", user_2=user,user=current_user, posts=post_exist)
            elif type == "3":
                team_exist = Team.query.filter_by(author=user.id).all()
                return render_template("view_user_posts.html", user_2=user,user=current_user, teams=team_exist)
            elif type == "4":
                player_exist = Player.query.filter_by(author=user.id).all()
                return render_template("view_user_posts.html", user_2=user,user=current_user, players=player_exist)
        elif page == "2":
            if type == "1":
                teams = Team.query.all()
                return render_template("portfolio_teams.html", user=current_user, teams = teams)
            elif type == "2":
                team_exist = Team.query.filter_by(type="National").all()
                return render_template("portfolio_teams.html", user=current_user, teams = team_exist)
            elif type == "3":
                team_exist = Team.query.filter_by(type="Club").all()
                return render_template("portfolio_teams.html", user=current_user, teams = team_exist)
        elif page == "3":
            if type == "1":
                players = Player.query.all()
                return render_template("portfolio_players.html", user=current_user, players = players)
            elif type == "2":
                player_exist = Player.query.filter_by(position = "GK").all()
                return render_template("portfolio_players.html", user=current_user, players = player_exist)
            elif type == "3":
                my_list = ["CB","RB","LB"]
                player_exist = Player.query.filter(Player.position.in_(my_list)).all()
                return render_template("portfolio_players.html", user=current_user, players = player_exist)
            elif type == "4":
                my_list = ["CM","CDM","CAM","LM","RM"]
                player_exist = Player.query.filter(Player.position.in_(my_list)).all()
                return render_template("portfolio_players.html", user=current_user, players = player_exist)
            elif type == "5":
                my_list = ["CF","ST","LW","RW"]
                player_exist = Player.query.filter(Player.position.in_(my_list)).all()
                return render_template("portfolio_players.html", user=current_user, players = player_exist)

@app.route('/user/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):

    user_to_delete= User.query.get_or_404(id)

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully", category="success")
        return redirect(url_for('home'))
    except:
        flash("Error!! ... looks that there was a problem", category="error")
        return redirect(url_for('home'))
    

@app.route('/user/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    flash ("You are logout", category="success")
    return redirect(url_for("home", user=current_user))


#  Post releated routes

@app.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    
    # Validate Form
    if request.method == "POST":

        title = request.form['title']
        slug = request.form['slug']
        content = request.form['content']
        image = request.files['image']

        title_exist = Post.query.filter_by(title=title).first()

        if title_exist:
            flash("Title aleready exist", category="error")
            return render_template("create_post.html", form=form,user=current_user)
        else:
            pic_file_name = secure_filename(image.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_file_name
            saver = request.files['image']

            post = Post(title=title, slug=slug, fk_user=current_user.id, content=content, post_pic=pic_name)

            db.session.add(post)
            db.session.commit()

            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

            flash("Post added successfully", category="success")

            return redirect(url_for('home'))
    else:
        return render_template("create_post.html", form=form,user=current_user)

@app.route('/post/view/<int:id>')
def view_post(id):
    post = Post.query.get_or_404(id)
    return render_template("view_post.html", post= post,user=current_user)

@app.route('/post/portfolio_post')
def view_all_post():
    post = Post.query.all()
    return render_template("portfolio_post.html", user=current_user,posts=post)


@app.route('/post/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):

    form = PostForm()
    post_to_update = Post.query.get_or_404(id)

    if request.method == "POST" and form.validate_on_submit(): 
        post_to_update.title = request.form['title']
        post_to_update.slug = request.form['slug']
        post_to_update.content = request.form['content']
        image = request.files['image']

        pic_file_name = secure_filename(image.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_file_name
        saver = request.files['image']

        post_to_update.post_pic = pic_name
        
        db.session.add(post_to_update)
        db.session.commit()

        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        flash("Post Updated Successfully",category="success")
        return redirect(url_for('home'))
    else:
        form.content.data = post_to_update.content
        return render_template("update_post.html", form=form, post_to_update=post_to_update, user=current_user)

@app.route('/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):

    post_to_delete= Post.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post deleted successfully", category="success")
        return redirect(url_for('home'))
    except:
        flash("Error!! ... looks that there was a problem", category="error")
        return redirect(url_for('home'))

#  Team releated routes

@app.route('/team/create', methods=['GET', 'POST'])
@login_required
def create_team():
    form = TeamForm()
    team =request.args.get("team", default="none")
    id =request.args.get("p_id", default="none")

    if request.method == "POST":

        name = request.form['name']
        text = request.form['text']
        palmares = request.form['palmares']
        image = request.files['image']
        type = request.form['type'] 

        pic_file_name = secure_filename(image.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_file_name
        saver = request.files['image']
        
        team = Team(name=name, text = text, fk_user = current_user.id , palmares = palmares, type = type , team_pic = pic_name)
        
        db.session.add(team)
        db.session.commit()

        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        flash("Team added successfully", category="success")

        if id != "none":
            player= Player.query.get_or_404(id)
            team.players.append(player)
            db.session.commit()

        return redirect(url_for('home'))
    else:
        if team != "none":
            form.name.data = team

        return render_template("create_team.html", form=form, user=current_user, team=team)

@app.route('/team/view/<int:id>')
def view_team(id):
    team = Team.query.get_or_404(id)
    return render_template("view_team.html", team=team,user=current_user)

@app.route('/team/portfolio_teams')
def view_all_teams():
    teams = Team.query.all()
    return render_template("portfolio_teams.html", user=current_user,teams=teams)

@app.route('/team/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_team(id):
    form = TeamForm()

    team_to_update = Team.query.get_or_404(id)

    if request.method == "POST": 
        team_to_update.name = request.form['name']
        team_to_update.text = request.form['text']
        team_to_update.palmares = request.form['palmares']
        image = request.files['image']
        team_to_update.type = request.form['type'] 

        pic_file_name = secure_filename(image.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_file_name
        saver = request.files['image']

        team_to_update.team_pic = pic_name

        db.session.add(team_to_update)
        db.session.commit()

        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        flash("Team Updated Successfully",category="success")
        return redirect(url_for('home'))
    else:
        form.name.data = team_to_update.name
        form.text.data = team_to_update.text
        form.palmares.data = team_to_update.palmares
        form.type.data = team_to_update.type 
        form.image.data = team_to_update.team_pic

        return render_template("update_team.html", form=form, team_to_update=team_to_update, user=current_user)

@app.route('/team/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_team(id):

    team_to_delete= Team.query.get_or_404(id)

    try:
        db.session.delete(team_to_delete)
        db.session.commit()
        flash("Team deleted successfully", category="success")
        return redirect(url_for('home'))
    except:
        flash("Error!! ... looks that there was a problem", category="error")
        return redirect(url_for('home'))  

#  Players releated routes

@app.route('/player/create', methods=['GET', 'POST'])
@login_required
def create_player():
    form = PlayerForm()
    teams = Team.query.order_by('name')
    group_list = []
    selected_options = []


    if teams:
        pair = (0, "New Team ( this will redirect you to the create team page after creating the player)")
        group_list.append(pair)
        for t in teams:
            pair = (t.id, t.name)
            group_list.append(pair)
    else:
        pair = (0, "New Team ( this will redirect you to the create team page after creating the player)")
        group_list.append(pair)

    form.team.choices = group_list

    if request.method == "POST" and form.validate_on_submit():
        selected_options = form.team.data
        length_options = len(selected_options)

        name = request.form['name']
        text = request.form['text']
        palmares = request.form['palmares']
        birth = request.form['birth']
        age = request.form['age']
        nationality = request.form['nationality']
        position = request.form['position'] 
        image = request.files['image']
        image_sm = request.files['image_sm']
        date_to_u = datetime.strptime(birth, '%Y-%m-%d').date()


        pic_file_name = secure_filename(image.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_file_name
        saver = request.files['image']

        pic_file_name_sm = secure_filename(image_sm.filename)
        pic_name_sm = str(uuid.uuid1()) + "_" + pic_file_name_sm
        saver_sm = request.files['image_sm']

        new_team = form.team_disp.data
        player = Player(name=name,text=text,palmares=palmares,birth=date_to_u,age=age,nationality=nationality,
                        position=position,player_pic=pic_name,player_small_pic=pic_name_sm,fk_user=current_user.id)
        db.session.add(player)
        db.session.commit()

        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        saver_sm.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name_sm))

        if length_options == 2:
            if selected_options[0] == 0:
                new_team = form.team_disp.data
                team_to_relate = Team.query.get_or_404(selected_options[1])
                team_to_relate.players.append(player)
                db.session.commit()
                form.team_disp.data =''

                flash('Player created but you will be redirected to created the new team', category='success')
                return redirect(url_for('create_team', user=current_user, team=new_team, p_id=player.id))
            else:
                team_to_relate = Team.query.get_or_404(selected_options[0])
                team_to_relate_2 = Team.query.get_or_404(selected_options[1])
                team_to_relate.players.append(player)
                team_to_relate_2.players.append(player)
                db.session.commit()

                flash('Player created successfully', category='success')
                return redirect(url_for('home'))
        else:
            if length_options == 1:
                if selected_options[0] == 0:
                    new_team = form.team_disp.data
                    db.session.commit()
                    form.team_disp.data =''

                    flash('Player created but you will be redirected to created the new team', category='success')
                    return redirect(url_for('create_team', user=current_user, team=new_team, p_id=player.id))
                else:
                    team_to_relate = Team.query.get_or_404(selected_options[0])
                    team_to_relate.players.append(player)
                    db.session.commit()

                    flash('Player updated successfully', category='success')
                    return redirect(url_for('home'))
    else:
        return render_template("create_player.html", form=form,user=current_user)

@app.route('/player/view/<int:id>')
def view_player(id):
    player = Player.query.get_or_404(id)
    return render_template("view_player.html", player=player,user=current_user)

@app.route('/player/portfolio_players')
def view_all_players():
    players = Player.query.all()
    return render_template("portfolio_players.html", user=current_user,players=players)


@app.route('/player/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_player(id):
    form = PlayerForm()
    player_to_update = Player.query.get_or_404(id)
    teams = Team.query.order_by('name')
    group_list = []
    selected_options = []

    if teams :
        pair = (0, "New Team ( this will redirect you to the create team page after creating the player)")
        group_list.append(pair)
        for t in teams:
            pair = (t.id, t.name)
            group_list.append(pair)
    else:
        pair = (0, "New Team ( this will redirect you to the create team page after creating the player)")
        group_list.append(pair)

    form.team.choices = group_list

    if request.method == "POST" and form.validate_on_submit(): 
        player_to_update.name = request.form['name']
        player_to_update.text = request.form['text']
        player_to_update.palmares = request.form['palmares']
        player_to_update.birth= request.form['birth']
        player_to_update.age = request.form['age']
        player_to_update.nationality = request.form['nationality']
        player_to_update.position = request.form['position']
        image = request.form['image']
        image_sm = request.form['sm']
        selected_options = form.team.data
        length_options = len(selected_options)
        
        pic_file_name = secure_filename(image.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_file_name
        saver = request.files['image']

        pic_file_name_sm = secure_filename(image_sm.filename)
        pic_name_sm = str(uuid.uuid1()) + "_" + pic_file_name_sm
        saver_sm = request.files['image_sm']

        player_to_update.player_pic = pic_name
        player_to_update.player_small_pic = pic_name_sm
        
        db.session.add(player_to_update)
        db.session.commit()

        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        saver_sm.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name_sm))

        player_to_update.plays.clear()

        if length_options == 2:
            if selected_options[0] == 0:
                new_team = request.form['team_disp']
                team_to_relate = Team.query.get_or_404(selected_options[1])
                team_to_relate.players.append(player_to_update)
                db.session.commit()
                form.team_disp.data =''

                flash('Player updated but you will be redirected to created the new team', category='success')
                return redirect(url_for('create_team', user=current_user, team=new_team, p_id=player_to_update.id))
            else:
                team_to_relate = Team.query.get_or_404(selected_options[0])
                team_to_relate_2 = Team.query.get_or_404(selected_options[1])
                team_to_relate.players.append(player_to_update)
                team_to_relate_2.players.append(player_to_update)
                db.session.commit()

                flash('Player updated successfully', category='success')
                return redirect(url_for('home'))
        else:
            if length_options == 1:
                if selected_options[0] == 0:
                    new_team = request.form['team_disp']
                    db.session.commit()
                    form.team_disp.data =''

                    flash('Player updated but you will be redirected to created the new team', category='success')
                    return redirect(url_for('create_team', user=current_user, team=new_team, p_id=player_to_update.id))
                else:
                    team_to_relate = Team.query.get_or_404(selected_options[0])
                    team_to_relate.players.append(player_to_update)
                    db.session.commit()

                    flash('Player updated successfully', category='success')
                    return redirect(url_for('home'))
    else:
        default_choices = []

        for p in player_to_update.plays:
            default_choices.append(p.id)

        form.name.data = player_to_update.name
        form.text.data = player_to_update.text
        form.palmares.data = player_to_update.palmares
        form.birth.data = player_to_update.birth 
        form.age.data = player_to_update.age
        form.nationality.data = player_to_update.nationality
        form.position.data = player_to_update.position
        form.team.data = default_choices

        return render_template("update_player.html", form=form, player_to_update=player_to_update,user=current_user)

@app.route('/player/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_player(id):

    player_to_delete= Player.query.get_or_404(id)

    try:
        db.session.delete(player_to_delete)
        db.session.commit()
        flash("Player deleted successfully", category="success")
        return redirect(url_for('home'))
    except:
        flash("Error!! ... looks that there was a problem", category="error")
        return redirect(url_for('home'))  

# Create error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error
@app.errorhandler(500)
def internal_server_errpr(e):
    return render_template("500.html"), 500