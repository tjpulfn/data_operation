import os
import bezier
import numpy as np


def four00Points(points):
    new_points = []
    for i in range(len(points) - 1):
        pi, pj = i, i + 1
        new_points.append(points[pi])
        center = ((points[pi][0] + points[pj][0]) / 2, (points[pi][1] + points[pj][1]) / 2)
        new_points.append(center)
    new_points.append(points[-1])
    return new_points

def approximate_curved_polygon(_contour, point_num=200):
    """
    使用贝塞尔曲线进行拟合,得到平滑的闭合多边形轮廓
    :param _contour: 构成多边形轮廓的点集. Array:(N, 2)
    :param point_num: 每次拟合的点的数量,越大则越平滑. Int
    :return: 返回平滑后的轮廓点
    """
    to_return_contour = []
    _contour = np.reshape(_contour, (-1, 2))
    # 复制起始点到最后,保证生成闭合的曲线
    # _contour = np.vstack((_contour, _contour[0, :].reshape((-1, 2))))
    for start_index in range(0, _contour.shape[0], point_num):
        # 多取一个点,防止曲线中间出现断点
        end_index = start_index + point_num + 1
        end_index = end_index if end_index < _contour.shape[0] else _contour.shape[0]
        nodes = np.transpose(_contour[start_index:end_index, :])
        # 拟合贝塞尔曲线
        curve = bezier.Curve(nodes, degree=nodes.shape[1] - 1)
        curve = curve.evaluate_multi(np.linspace(0.0, 1.0, point_num * 5))
        to_return_contour.append(np.transpose(curve))
    to_return_contour = np.array(to_return_contour).reshape((-1, 2))
    return to_return_contour

def select_seven_points(ori_points, len_pos, select_pos):
    points = ori_points
    while len(points) < len_pos:
        points = four00Points(points)
    points = np.array(points)
    res_point = approximate_curved_polygon(points)
    num = (len(res_point)) // select_pos
    mod = len(res_point) % select_pos
    new_points = []
    i = 0
    count = 0
    while i < len(res_point):
        new_points.append(res_point[i])
        if count == mod:
            i += num
        else:
            i += num + 1
            count += 1
    new_points.append(ori_points[-1])
    new_points = np.array(new_points)
    return new_points

def write_label_with_PgNet_old(fp, label_dict):
    write_line = ""
    for image_name in label_dict.keys():
        write_line = image_name + "\t"
        label_str = ""
        for num in label_dict[image_name].keys():
            content = label_dict[image_name][num]["content"]
            top_line = label_dict[image_name][num]["top_line"].tolist()
            end_line = label_dict[image_name][num]["end_line"].tolist()
            points = top_line + end_line
            write_str = "{" + '"{}": "{}", "{}": {}'.format("transcription", content, "points", points) + "}"
            if len(label_str) < 1:
                label_str = write_str
            else:
                label_str = label_str + ',' + write_str
        write_line = write_line + "[" + label_str + "]" + "\n"
    fp.write(write_line)

def write_label_with_PgNet(fp, label_dict):
    for image_name in label_dict.keys():
        seal_num = label_dict[image_name]["seal"]
        base_name = os.path.splitext(image_name)[0]
        for i in range(seal_num):
            seal_dict = []
            sub_seal_name = "{}_crop_{}.jpg".format(base_name, i + 1)
            seal_points = label_dict[image_name][sub_seal_name]
            seal_points = np.array(seal_points)
            x1, y1, x2, y2 = seal_points[0][0], seal_points[0][1], seal_points[1][0], seal_points[1][1] 
            scale = 0.3
            w, h = x2 - x1, y2 - y1
            new_x1, new_y1 = int(max(0, x1 - w * scale)), int(max(0, y1 - h * scale))
            for num in label_dict[image_name].keys():
                if num == "seal":
                    continue
                if base_name in num:
                    continue
                content = label_dict[image_name][num]["content"]
                top_line = label_dict[image_name][num]["top_line"].tolist()
                end_line = label_dict[image_name][num]["end_line"].tolist()
                points = top_line + end_line
                points1 = np.array(points)
                new_points = np.zeros(points1.shape, dtype=np.int32)
                new_points[:, 0] = points1[:, 0] - new_x1
                new_points[:, 1] = points1[:, 1] - new_y1
                min_x, max_x, min_y, max_y = min(points1[:,0]), max(points1[:,0]), min(points1[:,1]), max(points1[:,1])
                if min_x > x1 and max_x < x2 and min_y > y1 and max_y < y2:
                    seal_dict.append({"transcription": content, "points": new_points.tolist()})
            write_str = sub_seal_name + '\t' + str(seal_dict) + "\n"
            fp.write(write_str)

def feed_data(image_dict, data):
    image_name, number, content, new_points, top_line, end_line = data
    if number in image_dict[image_name]:
        if top_line:
            image_dict[image_name][number].update({"content": content, "top_line": new_points})
        if end_line:
            image_dict[image_name][number].update({"end_line": new_points})
    else:
        if top_line:
            image_dict[image_name].update({number:{"content": content, "top_line": new_points}})
        if end_line:
            image_dict[image_name].update({number:{"end_line": new_points}})
    return image_dict
