import time
from pymongo import MongoClient
from sympy.solvers import solve
from sympy import Symbol, Eq, sympify
from flask import Flask, render_template, request, jsonify, make_response
from flask_pymongo import PyMongo
from sympy.parsing.sympy_parser import *
import pymongo

app = Flask(__name__)

client =  MongoClient('localhost', 27017)

SolverDb = client.get_database('SolverDb')
SolverTable = SolverDb.SolverTable
LogTable = SolverDb.LogTable

x = Symbol('x')
y = Symbol('y')

def coefficients(eq):
    a,b,c=0,0,0
    x = Symbol('x')
    y = Symbol('y')
    z = Symbol('z')
    exp_eq = eq
    a = exp_eq.coeff(x,1)
    b = exp_eq.coeff(y,1)
    s = str(exp_eq)
    s = sympify(s)
    c = s.subs([(x,0),(y,0)])
    print(c)
    return (a, b, c);

def parsed_eq(equation):
    eq = equation.split('=')
    eq = eq[0]+'-'+eq[1]
    eq = parse_expr(eq, transformations='all')
    return eq

def step1(a,b,c):
    str =  "{a}*x = -({b}*y+({c})) "
    return ( str.format(a=a,b=b,c=c))
def step2(a,b,c):
    str = " x = -({b}*y+({c})) / ({a})"
    return ( str.format(a=a,b=b,c=c) )
def step3(a,b,c):
    str = "{b}*y = -({a}*x+({c}))"
    return ( str.format(a=a,b=b,c=c) )

def step4(a,b,c):
    str = " y = -({a}*x+({c})) / ({b}) "
    return ( str.format(a=a,b=b,c=c) )



@app.route("/", methods=["POST", "GET"]  )

def eq():
    if request.method == "POST":
        equation = request.form["equation"]
        LogTable.insert_one({'question': equation})

        # taking standard as ax+by+c = 0
        start = time.time()
        parsed_equation =  parsed_eq(equation)

        found = SolverDb.SolverTable.find_one( { "equation": str(parsed_equation)+'=0' } )
        if( found != None ):
            return str(found)

        # print("new")

        a,b,c = coefficients(parsed_equation)

        X = "x = "+ str(solve(parsed_equation , x , rational=True ))
        Y = "y = "+ str(solve(parsed_equation , y , rational=True ))

        Steps = {
            "Step1": step1(a, b, c),
            "Step2": step2(a, b, c),
            "Step3": step3(a, b, c),
            "step4": step4(a, b, c)
        }
        finish = time.time();


        solved = {
            'equation' : str(parsed_equation)+'=0' ,
            'steps' : Steps,
            'final_result' : X+", "+Y,
            'TotalTime' : finish - start
        }

        SolverTable.insert_one(solved)


        return make_response(jsonify(
            Equation = equation ,
            Steps = Steps ,
            FinalAnswer= X+" "+Y
        ),200)
    else:
        return render_template('eq.html')



if __name__ == '__main__':
    app.run( debug=True, Port=3002)