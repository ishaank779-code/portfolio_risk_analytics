import os, io, csv
from datetime import date
from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/portfolio_risk_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    asset_type = db.Column(db.String(40), nullable=False, default='Equity')
    sector = db.Column(db.String(80), nullable=False, default='Other')
    quantity = db.Column(db.Float, nullable=False, default=0)
    avg_cost = db.Column(db.Float, nullable=False, default=0)
    current_price = db.Column(db.Float, nullable=False, default=0)
    beta = db.Column(db.Float, nullable=False, default=1)
    created_at = db.Column(db.Date, nullable=False, default=date.today)
    @property
    def market_value(self): return self.quantity * self.current_price
    @property
    def cost_value(self): return self.quantity * self.avg_cost
    @property
    def pnl(self): return self.market_value - self.cost_value
    @property
    def pnl_pct(self): return (self.pnl / self.cost_value * 100) if self.cost_value else 0
    def as_dict(self):
        return {'id':self.id,'symbol':self.symbol,'name':self.name,'asset_type':self.asset_type,'sector':self.sector,'quantity':self.quantity,'avg_cost':self.avg_cost,'current_price':self.current_price,'beta':self.beta,'market_value':round(self.market_value,2),'cost_value':round(self.cost_value,2),'pnl':round(self.pnl,2),'pnl_pct':round(self.pnl_pct,2)}

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id', ondelete='SET NULL'), nullable=True)
    symbol = db.Column(db.String(16), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.String(250), nullable=True)
    def as_dict(self): return {'id':self.id,'asset_id':self.asset_id,'symbol':self.symbol,'transaction_type':self.transaction_type,'quantity':self.quantity,'price':self.price,'transaction_date':self.transaction_date.isoformat(),'notes':self.notes or ''}

@app.get('/')
def index(): return render_template('index.html')

@app.get('/api/health')
def health():
    try: db.session.execute(db.text('SELECT 1')); return jsonify({'status':'ok','database':'connected'})
    except Exception as e: return jsonify({'status':'error','database':'disconnected','detail':str(e)}), 503

@app.get('/api/assets')
def list_assets():
    q=request.args.get('q','').strip(); typ=request.args.get('type','').strip()
    query=Asset.query
    if q: query=query.filter(db.or_(Asset.symbol.ilike(f'%{q}%'),Asset.name.ilike(f'%{q}%'),Asset.sector.ilike(f'%{q}%')))
    if typ: query=query.filter_by(asset_type=typ)
    return jsonify([a.as_dict() for a in query.order_by(Asset.symbol).all()])

@app.post('/api/assets')
def create_asset():
    d=request.get_json(silent=True) or {}
    required=['symbol','name','asset_type','sector','quantity','avg_cost','current_price','beta']
    if any(d.get(k) in (None,'') for k in required): return jsonify({'error':'Please complete all required fields.'}),400
    try:
        a=Asset(symbol=d['symbol'].strip().upper(),name=d['name'].strip(),asset_type=d['asset_type'],sector=d['sector'].strip(),quantity=float(d['quantity']),avg_cost=float(d['avg_cost']),current_price=float(d['current_price']),beta=float(d['beta']))
        if min(a.quantity,a.avg_cost,a.current_price,a.beta)<0: return jsonify({'error':'Numeric values cannot be negative.'}),400
        db.session.add(a); db.session.commit(); return jsonify(a.as_dict()),201
    except Exception as e: db.session.rollback(); return jsonify({'error':'Could not save asset. Check that the ticker is unique and values are valid.'}),400

@app.put('/api/assets/<int:asset_id>')
def update_asset(asset_id):
    a=Asset.query.get_or_404(asset_id); d=request.get_json(silent=True) or {}
    try:
        for k in ['symbol','name','asset_type','sector']:
            if k in d: setattr(a,k,d[k].strip().upper() if k=='symbol' else d[k].strip())
        for k in ['quantity','avg_cost','current_price','beta']:
            if k in d: setattr(a,k,float(d[k]))
        if min(a.quantity,a.avg_cost,a.current_price,a.beta)<0: return jsonify({'error':'Numeric values cannot be negative.'}),400
        db.session.commit(); return jsonify(a.as_dict())
    except Exception: db.session.rollback(); return jsonify({'error':'Update failed. Check values and ticker uniqueness.'}),400

@app.delete('/api/assets/<int:asset_id>')
def delete_asset(asset_id):
    a=Asset.query.get_or_404(asset_id)
    Transaction.query.filter_by(asset_id=a.id).update({'asset_id':None})
    db.session.delete(a); db.session.commit(); return jsonify({'message':'Asset deleted.'})

@app.get('/api/transactions')
def list_transactions():
    return jsonify([t.as_dict() for t in Transaction.query.order_by(Transaction.transaction_date.desc(),Transaction.id.desc()).limit(100).all()])

@app.post('/api/transactions')
def create_transaction():
    d=request.get_json(silent=True) or {}
    try:
        a=Asset.query.filter_by(symbol=d.get('symbol','').strip().upper()).first()
        if not a: return jsonify({'error':'Asset ticker was not found. Add the asset first.'}),400
        typ=d.get('transaction_type','').upper(); qty=float(d.get('quantity',0)); price=float(d.get('price',0))
        if typ not in ('BUY','SELL') or qty<=0 or price<=0: return jsonify({'error':'Choose BUY or SELL and enter positive quantity and price.'}),400
        if typ=='SELL' and qty>a.quantity: return jsonify({'error':'Sell quantity exceeds current holdings.'}),400
        if typ=='BUY':
            total=a.quantity+qty; a.avg_cost=((a.quantity*a.avg_cost)+(qty*price))/total if total else price; a.quantity=total
        else: a.quantity-=qty
        t=Transaction(asset_id=a.id,symbol=a.symbol,transaction_type=typ,quantity=qty,price=price,transaction_date=date.fromisoformat(d.get('transaction_date') or date.today().isoformat()),notes=(d.get('notes') or '')[:250])
        db.session.add(t); db.session.commit(); return jsonify({'transaction':t.as_dict(),'asset':a.as_dict()}),201
    except Exception: db.session.rollback(); return jsonify({'error':'Invalid transaction details.'}),400

@app.get('/api/summary')
def summary():
    assets=Asset.query.all(); total=sum(a.market_value for a in assets); cost=sum(a.cost_value for a in assets); pnl=total-cost
    exposure=sum(a.market_value*a.beta for a in assets)/total if total else 0
    sectors={}
    types={}
    for a in assets:
        sectors[a.sector]=sectors.get(a.sector,0)+a.market_value
        types[a.asset_type]=types.get(a.asset_type,0)+a.market_value
    return jsonify({'market_value':round(total,2),'cost_value':round(cost,2),'pnl':round(pnl,2),'pnl_pct':round(pnl/cost*100,2) if cost else 0,'holdings':len(assets),'weighted_beta':round(exposure,2),'sector_allocation':sectors,'asset_allocation':types,'top_assets':[a.as_dict() for a in sorted(assets,key=lambda x:x.market_value,reverse=True)[:5]],'risk_level':'High' if exposure>=1.25 else 'Moderate' if exposure>=0.85 else 'Lower'})

@app.get('/api/export/assets.csv')
def export_assets():
    output=io.StringIO(); writer=csv.DictWriter(output,fieldnames=['symbol','name','asset_type','sector','quantity','avg_cost','current_price','market_value','pnl','pnl_pct','beta']); writer.writeheader()
    for a in Asset.query.order_by(Asset.symbol).all(): writer.writerow({k:a.as_dict().get(k) for k in writer.fieldnames})
    return Response(output.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=portfolio_holdings.csv'})

@app.cli.command('seed-demo')
def seed_demo():
    """Insert fictional demo holdings; run: flask --app app seed-demo"""
    if Asset.query.count(): print('Assets already exist; skipping demo seed.'); return
    rows=[('AAPL','Apple Inc.','Equity','Technology',12,172,189.5,1.2),('MSFT','Microsoft Corp.','Equity','Technology',8,390,421.2,0.9),('JPM','JPMorgan Chase','Equity','Financials',15,180,196.4,1.1),('NVDA','NVIDIA Corp.','Equity','Semiconductors',10,105,121.8,1.7),('BND','Total Bond Market ETF','ETF','Fixed Income',25,71,72.3,0.2),('GLD','Gold Trust ETF','ETF','Commodities',9,185,191.1,0.1)]
    for r in rows: db.session.add(Asset(symbol=r[0],name=r[1],asset_type=r[2],sector=r[3],quantity=r[4],avg_cost=r[5],current_price=r[6],beta=r[7]))
    db.session.commit(); print('Inserted fictional demo assets.')

if __name__=='__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
