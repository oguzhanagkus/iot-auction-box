import json
import websockets
import websockets.exceptions
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from . import database
from .models import User, Item, Transaction, Coupon

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    user = User.query.filter_by(id=current_user.id).first()
    return render_template("home.html", title="Home", balance=user.balance)


@views.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        return render_template("sell.html", title="Sell")
    else:
        name = request.form.get("name")
        price = int(request.form.get("price"))
        description = request.form.get("description")
        owner = current_user.id
        hw_id = request.args.get("hw_id")

        item = Item.query.filter_by(on_sale=True, hw_id=hw_id).first()
        if not item:
            new_item = Item(name=name, price=price, description=description, owner=owner, hw_id=hw_id)
            database.session.add(new_item)
            database.session.commit()
            flash("Item added!", category="success")
            return redirect(url_for("views.device", command="lock", hw_id=hw_id, name=name, price=price))
        else:
            flash("There is an item already.")
            return redirect(url_for('views.home'))


@views.route("/purchase", methods=["GET", "POST"])
@login_required
def purchase():
    if request.method == "GET":
        hw_id = request.args.get("hw_id")
        item = Item.query.filter_by(on_sale=True, hw_id=hw_id).first()
        return render_template("purchase.html", title="Purchase", name=item.name, price=item.price,
                               description=item.description)
    else:
        hw_id = request.args.get("hw_id")
        item = Item.query.filter_by(on_sale=True, hw_id=hw_id).first()

        if item:
            purchaser = User.query.filter_by(id=current_user.id).first()
            seller = User.query.filter_by(id=item.owner).first()
            if purchaser.balance > item.price:
                purchaser.balance -= item.price
                seller.balance += item.price
                item.on_sale = False
                item.owner = purchaser.id
                transaction = Transaction(item.price, purchaser.id, seller.id, item.id)
                database.session.add(transaction)
                database.session.commit()
                flash("Purchase completed!", category="success")
                return redirect(url_for("views.device", command="unlock", hw_id=hw_id))
            else:
                flash("You have not enough balance to purchase!", category="error")
        else:
            flash("There is no item!", category="error")
        return redirect(url_for('views.home'))


@views.route("/load_balance", methods=["GET", "POST"])
@login_required
def load_balance():
    if request.method == "GET":
        return render_template("load_balance.html", title="Load Balance")
    else:
        code = request.form.get("code")
        coupon = Coupon.query.filter_by(code=code, used=False).first()
        user = User.query.filter_by(id=current_user.id).first()

        if coupon:
            user.balance += coupon.amount
            coupon.used = True
            coupon.used_by = user.id
            database.session.commit()
            flash("Balance updated!", category="success")
        else:
            flash("Invalid code!", category="error")
        return redirect(url_for('views.home'))


@views.route("/device")
@login_required
async def device():
    command = request.args.get("command")
    hw_id = request.args.get("hw_id")
    name = request.args.get("name")
    price = request.args.get("price")
    await send_command(command, hw_id, name, price)
    return redirect(url_for('views.home'))


async def send_command(command, hw_id, item_name, item_price):
    async with websockets.connect(f"ws://159.65.118.24:8765") as websocket:
        try:
            event = {
                "type": "command", "hw_id": hw_id, "command": command,
                "item": {"name": item_name, "price": item_price}
            }
            await websocket.send(json.dumps(event))

            while True:
                message = await websocket.recv()
                event = json.loads(message)

                if event["type"] == "response":
                    print(event["message"])
                else:
                    print("invalid event")
        except websockets.exceptions.ConnectionClosedOK:
            print("connection closed")
        except Exception as e:
            print(e)
