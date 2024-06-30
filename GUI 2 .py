import streamlit as st
import csv
import io

def ftta_algorithm(tasks, deadlines, num_vms):
    avg_execution_times = []
    priorities = []
    task_assignment_times = []  # To store task assignment times
    busy_vms = [False] * num_vms  # To track busy virtual machines

    for i in range(len(tasks)):
        avg_exec_time = sum(tasks[i]) / len(tasks[i])
        avg_execution_times.append(avg_exec_time)
        priority = deadlines[i] - avg_exec_time
        priorities.append(priority)
    
    task_info = list(zip(range(len(tasks)), tasks, avg_execution_times, priorities, deadlines))
    task_info.sort(key=lambda x: x[3])
    
    ready_list = task_info[:]
    rejected_list = []
    step = 1
    vm_execution_times = [0] * num_vms
    results = []
    header = f"<tr><th>Step</th><th>Ready list</th><th>Task selected</th><th>Execution time</th><th>Deadline</th><th>VM selected</th></tr>"
    results.append(header)
    
    while ready_list:
        task_data = ready_list.pop(0)
        task_index, task, avg_exec_time, priority, deadline = task_data
        min_vm_index = min(range(len(vm_execution_times)), key=lambda j: vm_execution_times[j] + task[j])
        min_exec_time = task[min_vm_index]
        
        # Record task assignment time
        task_assignment_times.append((f"T{task_index}", step, f"VM{min_vm_index + 1}"))

        if min_exec_time <= deadline:
            vm_execution_times[min_vm_index] += min_exec_time
            busy_vms[min_vm_index] = True
            vm_selected = f"VM{min_vm_index + 1}"
        else:
            result, vm_selected = algorithm_2(task_index, task, deadline, tasks, deadlines, vm_execution_times)
            if not result:
                rejected_list.append(task_index)
                vm_selected = "Rejected"
        
        ready_list_str = ', '.join([f"T{t[0]}" for t in ready_list])
        exec_time_str = ', '.join(map(str, task))
        row = f"<tr><td>{step}</td><td>{ready_list_str}</td><td>T{task_index}</td><td>{exec_time_str}</td><td>{deadline}</td><td>{vm_selected}</td></tr>"
        results.append(row)
        step += 1
    
    # Display busy virtual machines
    busy_vms_info = [f"VM{idx + 1}" for idx, busy in enumerate(busy_vms) if busy]
    if busy_vms_info:
        busy_vms_str = ", ".join(busy_vms_info)
    else:
        busy_vms_str = "None"

    html_table = f"<table>{''.join(results)}</table>"
    return html_table, task_assignment_times, busy_vms_str

def algorithm_2(task_index, task, deadline, tasks, deadlines, vm_execution_times):
    L1 = sorted(range(len(vm_execution_times)), key=lambda j: vm_execution_times[j] + task[j])
    L2 = sorted([i for i in range(len(vm_execution_times)) if i not in L1], key=lambda j: vm_execution_times[j] + task[j])

    flag = False

    for vm1 in L1:
        if task[vm1] <= deadline:
            can_schedule = True
            for other_task_index, other_task in enumerate(tasks):
                if other_task_index != task_index:
                    other_task_execution_time = other_task[vm1]
                    if vm_execution_times[vm1] + task[vm1] <= deadlines[task_index] and vm_execution_times[vm1] + task[vm1] + other_task_execution_time <= deadlines[other_task_index]:
                        vm_execution_times[vm1] += task[vm1]
                        return True, f"VM{vm1 + 1}"
                    else:
                        can_schedule = False
            if can_schedule:
                vm_execution_times[vm1] += task[vm1]
                return True, f"VM{vm1 + 1}"

    if not flag:
        for vm1 in L1:
            for vm2 in L2:
                if task[vm1] <= deadline and task[vm2] <= deadline:
                    task_time = task[vm1]
                    for other_task_index, other_task in enumerate(tasks):
                        if other_task_index != task_index:
                            other_task_execution_time = other_task[vm1]
                            if vm_execution_times[vm1] + task[vm1] <= deadlines[task_index] and vm_execution_times[vm1] + task[vm1] + other_task_execution_time <= deadlines[other_task_index]:
                                vm_execution_times[vm2] += task_time
                                vm_execution_times[vm1] -= task_time
                                return True, f"VM{vm2 + 1} (migrated from VM{vm1 + 1})"
        return False, None

st.title("FTTA Algorithm")

st.sidebar.header("Input Parameters")

num_tasks = st.sidebar.number_input("Number of Tasks", min_value=1, value=5)
num_vms = st.sidebar.number_input("Number of VMs", min_value=1, value=2)

tasks = []
deadlines = []

st.sidebar.header("Tasks and Deadlines")

for i in range(num_tasks):
    task = st.sidebar.text_input(f"Task {i+1} (comma-separated execution times)", key=f"task_{i}")
    deadline = st.sidebar.number_input(f"Deadline {i+1}", key=f"deadline_{i}", value=10)
    
    if task:
        try:
            task = list(map(int, task.split(',')))
            tasks.append(task)
        except ValueError:
            st.sidebar.error(f"Invalid input for task {i+1}. Please use commas to separate the execution times.")
            tasks = []
            break
    else:
        tasks = []
        break

    deadlines.append(deadline)

if st.sidebar.button("Run FTTA"):
    if tasks and deadlines:
        results, task_assignment_times, busy_vms_str = ftta_algorithm(tasks, deadlines, num_vms)
        
        st.markdown(
            f"""
            <div style="overflow-x: auto;">
                {results}
            </div>
            """
            , unsafe_allow_html=True
        )
        
        # Display task assignment times in a table
        st.markdown("**Task Assignment Times**")
        task_assignment_results = []
        task_assignment_results.append("<table><tr><th>Task</th><th>Step</th><th>VM</th></tr>")
        for task, step, vm in task_assignment_times:
            task_assignment_results.append(f"<tr><td>{task}</td><td>{step}</td><td>{vm}</td></tr>")
        task_assignment_results.append("</table>")
        task_assignment_table = ''.join(task_assignment_results)
        st.markdown(task_assignment_table, unsafe_allow_html=True)
        
        # Display busy virtual machines in a table
        st.markdown("**Busy Virtual Machines**")
        busy_vms_table = "<table><tr><th>VM</th></tr>"
        if busy_vms_str == "None":
            busy_vms_table += "<tr><td>None</td></tr>"
        else:
            for vm in busy_vms_str.split(","):
                busy_vms_table += f"<tr><td>{vm.strip()}</td></tr>"
        busy_vms_table += "</table>"
        st.markdown(busy_vms_table, unsafe_allow_html=True)
    else:
        st.error("Please provide valid inputs for all tasks and deadlines.")

st.sidebar.header("Load Tasks from File")

uploaded_file = st.sidebar.file_uploader("Choose a file (CSV or TXT)", type=["csv", "txt"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            # Read CSV file
            reader = csv.reader(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
            lines = list(reader)
            num_tasks = len(lines)
            tasks = []
            deadlines = []
            for i in range(num_tasks):
                task = list(map(int, lines[i][0].strip().split(',')))
                deadline = int(lines[i][1].strip())
                tasks.append(task)
                deadlines.append(deadline)
            st.sidebar.success(f"Loaded {num_tasks} tasks from CSV file.")
        else:
            # Read plain text file
            lines = uploaded_file.getvalue().decode("utf-8").splitlines()
            num_tasks = len(lines) // 2
            tasks = []
            deadlines = []
            for i in range(num_tasks):
                task = list(map(int, lines[i].strip().split(',')))
                deadline = int(lines[num_tasks + i].strip())
                tasks.append(task)
                deadlines.append(deadline)
            st.sidebar.success(f"Loaded {num_tasks} tasks from TXT file.")

        if st.sidebar.button("Run FTTA with File Data"):
            if tasks and deadlines:
                results, task_assignment_times, busy_vms_str = ftta_algorithm(tasks, deadlines, num_vms)
                
                st.markdown(
                    f"""
                    <div style="overflow-x: auto;">
                        {results}
                    </div>
                    """
                    , unsafe_allow_html=True
                )
                
                # Display task assignment times in a table
                st.markdown("**Task Assignment Times**")
                task_assignment_results = []
                task_assignment_results.append("<table><tr><th>Task</th><th>Step</th><th>VM</th></tr>")
                for task, step, vm in task_assignment_times:
                    task_assignment_results.append(f"<tr><td>{task}</td><td>{step}</td><td>{vm}</td></tr>")
                task_assignment_results.append("</table>")
                task_assignment_table = ''.join(task_assignment_results)
                st.markdown(task_assignment_table, unsafe_allow_html=True)
                
                # Display busy virtual machines in a table
                st.markdown("**Busy Virtual Machines**")
                busy_vms_table = "<table><tr><th>VM</th></tr>"
                if busy_vms_str == "None":
                    busy_vms_table += "<tr><td>None</td></tr>"
                else:
                    for vm in busy_vms_str.split(","):
                        busy_vms_table += f"<tr><td>{vm.strip()}</td></tr>"
                busy_vms_table += "</table>"
                st.markdown(busy_vms_table, unsafe_allow_html=True)
            else:
                st.error("Invalid file data.")
    except Exception as e:
        st.sidebar.error(f"Error reading file: {e}")
