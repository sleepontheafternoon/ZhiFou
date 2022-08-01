from pyecharts.charts import Line
import pyecharts.options as opts
from pyecharts.charts import Grid

def DrawLine(x_y_unit,sid,path="basic_line_chart.html"):
    x = list(x_y_unit.keys())
    y = list(x_y_unit.values())

    grid = Grid()

    line = (

        Line(init_opts=opts.InitOpts(width="1200px"))

        # 进行全局设置
        .set_global_opts(
            tooltip_opts=opts.TooltipOpts(is_show=True),  # 显示提示信息,默认为显示,可以不写
            title_opts=opts.TitleOpts(title="学生知识点掌握情况",pos_left="15%"),
            xaxis_opts=opts.AxisOpts(type_="category",axislabel_opts={"interval":"0","rotate":45}),
            yaxis_opts=opts.AxisOpts(
                type_="value",

                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
        )
        # 添加x轴的点
        .add_xaxis(xaxis_data=x)

        # 添加y轴的点
        .add_yaxis(
            series_name="",
            y_axis=y,
            symbol="emptyCircle",
            is_symbol_show=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
        # 保存为一个html文件

    )

    grid.add(line, grid_opts=opts.GridOpts(pos_bottom="22%",pos_left="25%",pos_right="30px"))
    grid.render(str(sid)+path)