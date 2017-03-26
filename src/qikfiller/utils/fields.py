import sys

from qikfiller.cache.orm import Task


def get_field(session, table, field):
    if table is Task:
        return get_task_field(session, field)
    print("validating {table} from {task_id}:".format(table=table.__tablename__, task_id=field))
    if not isinstance(field, int):
        fields = session.query(table).filter(table.name.ilike('%{field}%'.format(field=field))).all()
        if len(fields) == 0:
            print('  Could not find any {table} matching "{field}"'.format(table=table.__tablename__, field=field))
            sys.exit(1)
        elif len(fields) > 1:
            t = [('{field_.id}'.format(field_=field_), '{field_.name}'.format(field_=field_)) for field_ in fields]
            l = [max(len(x[y]) for x in t) for y in range(len(t[0]))]
            for type_ in t:
                print('  {{0:>{0}s}}: {{1:<{1}s}}'.format(*l).format(*type_))
            field = int(input('  Please enter the id of desired {table} from above: '
                              .format(table=table.__class__.__name__.lower())))
        else:
            field = fields[0].id
    print('    Got {}'.format(session.query(table).get(field)))
    return field


def get_task_field(session, task_id):
    print("validating Task from {task_id}:".format(task_id=task_id))
    if not isinstance(task_id, int):
        task_id_split = task_id.split(':')
        if task_id_split[-1]:
            tasks = session.query(Task) \
                .filter(Task.name.ilike('%{task_id_split}%'.format(task_id_split=task_id_split[-1]))).all()
        else:
            tasks = session.query(Task).all()
        if len(task_id_split) == 2:
            tasks = [task for task in tasks if task_id_split[0].lower() in task.get_client().name.lower()]
        if len(tasks) == 0:
            print('  Could not find any task matching "{task_id}"'.format(task_id=task_id))
            sys.exit(1)
        elif len(tasks) > 1:
            t = [(
                '{task_id}'.format(task_id=task.id),
                '{client}'.format(client=task.get_client().name),
                '{task_name}'.format(task_name=task.name)
            ) for task in tasks]
            l = [max(len(x[y]) for x in t) for y in range(len(t[0]))]
            for type_ in t:
                print('  {{0:>{0}s}}: {{1:<{1}s}}: {{2:<{2}s}}'.format(*l).format(*type_))
            task_id = int(input('  Please enter the id of desired task from above: '))
        else:
            task_id = tasks[0].id
        print('    Got {}'.format(session.query(Task).get(task_id)))
    return task_id
