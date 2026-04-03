from flask import Flask, render_template, request
import pyodbc

app = Flask(__name__)

# ✅ SQL Connection (with timeout)
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAPTOP-4N3VK7RO;"
    "Database=task;"
    "Trusted_Connection=yes;",
    timeout=5
)
cursor = conn.cursor()


# ✅ Work Type based on complexity
def get_work_type(complexity):
    if complexity <= 3:
        return "Testing"
    elif complexity <= 6:
        return "Bug Fixing"
    else:
        return "Development"


# ✅ Home Page
@app.route("/")
def home():
    return render_template("index.html")


# ✅ Search Employee
@app.route("/search", methods=["POST"])
def search():
    try:
        name = request.form["name"]

        cursor.execute(
            "SELECT name, skill, workload, work_type FROM employees WHERE name=?",
            (name,)
        )
        data = cursor.fetchone()

        return render_template("result.html", data=data)

    except Exception as e:
        return f"Error: {e}"


# ✅ Update Workload Count
@app.route("/update", methods=["POST"])
def update():
    try:
        name = request.form["name"]
        workload_count = int(request.form["workload"])

        cursor.execute(
            "UPDATE employees SET workload_count=? WHERE name=?",
            (workload_count, name)
        )
        conn.commit()

        return "<h2>Updated Successfully</h2><a href='/'>Back</a>"

    except Exception as e:
        return f"Error: {e}"


# 🚀 Smart Allocation (FINAL FIXED)
@app.route("/allocate", methods=["POST"])
def allocate():
    try:
        print("Step 1: Request received")

        skill = request.form["skill"].strip()
        complexity = int(request.form["complexity"])

        print("Step 2: Input:", skill, complexity)

        # 🔹 Get employees (safe + fast)
        cursor.execute("""
            SELECT TOP 50 name, skill, workload_count, workload, work_type
            FROM employees
            WHERE LOWER(skill) LIKE LOWER(?)
        """, ('%' + skill + '%',))

        print("Step 3: Query executed")

        employees = cursor.fetchall()

        print("Step 4: Employees fetched:", len(employees))

        if employees:

            # 🔹 Handle NULL workload_count safely
            best = min(employees, key=lambda x: x[2] if x[2] is not None else 999)

            emp_name = best[0]
            emp_skill = best[1]
            current_count = best[2] if best[2] else 0
            current_tasks = best[3] if best[3] else ""

            # 🔹 Get new task
            new_task = get_work_type(complexity)

            # 🔹 Append task
            if current_tasks:
                updated_tasks = current_tasks + ", " + new_task
            else:
                updated_tasks = new_task

            new_count = current_count + 1

            print("Step 5: Selected:", emp_name)

            # 🔹 Update DB
            cursor.execute("""
                UPDATE employees
                SET workload_count=?, workload=?, work_type=?
                WHERE name=?
            """, (new_count, updated_tasks, new_task, emp_name))

            conn.commit()

            print("Step 6: Updated successfully")

            return render_template(
                "result.html",
                emp_name=emp_name,
                emp_skill=emp_skill,
                workload=updated_tasks,
                work_type=new_task
            )

        else:
            print("No employees found")
            return "<h2>No employee found</h2><a href='/'>Back</a>"

    except Exception as e:
        print("Error:", e)
        return f"Error: {e}"


# 📋 View Employees
@app.route("/employees")
def employees_list():
    try:
        cursor.execute("""
            SELECT name, skill, workload_count, workload, work_type
            FROM employees
        """)
        data = cursor.fetchall()

        return render_template("employees.html", data=data)

    except Exception as e:
        return f"Error: {e}"


# ✅ Run App
if __name__ == "__main__":
    app.run(debug=True)
