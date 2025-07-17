import coolNewLanguage.src as hilt
from uh import get_current_best_pt, generate_S
from structure.hyperplane import Hyperplane
from structure.hyperplane_set import HyperplaneSet
from structure.point import Point
from structure.point_set import PointSet
from structure import others
tool = hilt.Tool('interactive_search')
tool.state['state_initialized'] = False
def upload_dataset():
    file = hilt.FileUploadComponent('.txt', label="Upload a dataset file:")
    if tool.user_input_received():
        tool.state['pointset'] = PointSet(file.value)
tool.add_stage('upload_dataset', upload_dataset)
def iterate():
    if not tool.state['state_initialized']:
        pset = tool.state['pointset']
        tool.state['dim'] = pset.points[0].dim
        tool.state['num_question'] = 0
        tool.state['rr'] = 1
        tool.state['C_idx'] = [i for i in range(len(pset.points))]
        C_idx = tool.state['C_idx']
        tool.state['hset'] = HyperplaneSet(tool.state['dim'])
        hset = tool.state['hset']
        tool.state['current_best_idx'] = get_current_best_pt(pset.points, C_idx, hset)
        tool.state['last_best'] = -1
        tool.state['frame'] = []
        tool.state['u'] = Point(pset.points[0].dim)
        tool.state['state_initialized'] = True
    C_idx = tool.state['C_idx']
    print(f"CIDX LENGTH: {len(C_idx)}")
    print(f"RR: {tool.state['rr']}")
    rr = tool.state['rr']
    epsilon = 0.1
    maxRound = 60
    num_question = tool.state['num_question']
    hset = tool.state['hset']
    pset = tool.state['pointset']
    if len(C_idx) <= 1 or not (rr > epsilon and not others.isZero(rr - epsilon)) or num_question >= maxRound: # if done, show result
        result = pset.points[get_current_best_pt(pset.points, C_idx, hset)]
        result_point = pset.points[result.id]
        data_group_2 = result_point.coord.tolist()
        hilt.TextComponent("Search completed:")
        hilt.TextComponent(f"Year: {data_group_2[0]}, Price: {data_group_2[1]}, Mileage: {data_group_2[2]}, Tax: {data_group_2[3]}, Engine Size: {data_group_2[4]}")
    else:
        C_idx.sort()
        P = pset.points
        s = 2
        hset = tool.state['hset']
        current_best_idx = tool.state['current_best_idx']
        last_best = tool.state['last_best']
        frame = tool.state['frame']
        cmp_option = 2
        S = generate_S(P, C_idx, s, current_best_idx, last_best, frame, cmp_option)
        p1 = P[C_idx[S[0]]]
        p2 = P[C_idx[S[1]]]
        data_group_1 = p1.coord.tolist()
        data_group_2 = p2.coord.tolist()
        hilt.TextComponent(f"Question {num_question}:")
        hilt.TextComponent(f"CHOICE 1: Year: {data_group_1[0]}, Price: {data_group_1[1]}, Mileage: {data_group_1[2]}, Tax: {data_group_1[3]}, Engine Size: {data_group_1[4]}")
        hilt.TextComponent(f"CHOICE 2: Year: {data_group_2[0]}, Price: {data_group_2[1]}, Mileage: {data_group_2[2]}, Tax: {data_group_2[3]}, Engine Size: {data_group_2[4]}")
        choice_component = hilt.SelectorComponent(["Choice 1", "Choice 2"], "Pick a choice:")
        if tool.user_input_received():
            tool.state['num_question'] += 1
            choice = 1 if choice_component.value == "Choice 1" else 2
            max_idx = S[0] if choice == 1 else S[1]
            last_best = current_best_idx
            current_best_idx = C_idx[max_idx]
            for i in S:
                if max_idx == i:
                    continue
                tmp = Hyperplane(p1=P[C_idx[i]], p2=P[C_idx[max_idx]])
                C_idx[i] = -1
                hset.hyperplanes.append(tmp)
            hset.set_ext_pts()
            C_idx = list(filter(lambda x: x != -1, C_idx))
            tool.state['C_idx'] = C_idx
            tool.state['last_best'] = last_best
            tool.state['current_best_idx'] = current_best_idx
            if len(C_idx) == 1: return
            C_idx, rr = hset.rtree_prune(pset.points, C_idx, 2)
            tool.state['C_idx'] = C_idx
            tool.state['rr'] = rr
tool.add_stage('iterate', iterate)
tool.run()