/**
 * 用于判断数组中是否包含键为key，值为value的dict，若有则返回索引，没有则返回-1
 * @param array 数组，数组中包含着是字典
 * @param key 键名
 * @param value 值
 * @return {int} 索引，若不存在则返回-1
 */
function contains(array, key, value){
    for (let i = 0; i < array.length; i++){
        let data = array[i];
        if (data[key] == value)
            return i;
    }
    return -1;
}
/**
 * 联系数组中是否包含对应的联系，
 * @param links 联系数组
 * @param link 联系 {source:0, target: 1}
 * @return {number} 若有，则返回对应的索引；否则返回-1
 */
function containslink(links, link) {
    for (let i = 0; i < links.length; i++){
        let l = links[i];
        if (l.source == link.source && l.target == link.target){
            return i;
        }
    }
    return -1;
}
/**
 * 处理老师和和做人的关系
 * @param self {id: id, name: name} 个人信息
 */
function handle_partner_relations(self, titles) {
    //每个类别所对应的颜色
    let colors = ["#ee6a50", "#4f94cd", "#daa520", "#0000ff", "#8fbc8f", "#5d478b", "#528b8b", "#483d8b", "#3a5fcd"];
    let categories = [];
    let links = [];
    let nodes = [];
    let kinds = [];

    let title = '未知';
    if (self.name in titles){
        title = titles[self.name].honors[0].title;
    }
    categories.push({"name": title, "color": colors[0]});
    nodes.push({"name": self.name, "category": 0});
    kinds.push(self.name);

    d3.selectAll("#authors").each(function (d, i, all) {
        let array = JSON.parse(all[i].innerHTML);
        console.log(array);

        for (let i = 0; i < array.length; i++){
            let name = array[i].name;
            if (name == self.name)
                continue;
            //获取头衔
            title = '未知';
            if (name in titles){
                title = titles[name].honors[0].title;
            }
            //插入类别
            let index = kinds.indexOf(title);
            if (index == -1){
                kinds.push(title);
                index = kinds.length - 1;
                categories.push({"name": title, "color": colors[categories.length]});
            }
            //尝试添加节点
            let nodeindex = contains(nodes, 'name', name);
            //不存在对应的点，则添加
            if (nodeindex == -1){
                nodes.push({
                    category: index,
                    'name': name,
                });
                nodeindex = nodes.length - 1;
            }
            //尝试添加联系
            let link = {source: 0, target: nodeindex, width: 1};
            let linkindex = containslink(links, link);
            //不存在，则添加
            if (linkindex == -1){
                links.push(link);
            }else{
                links[linkindex].width += 1;
            }
        }
    });
    return {
        "categories": categories,
        "nodes": nodes,
        "links": links,
    };
}

