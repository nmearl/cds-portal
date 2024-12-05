from pathlib import Path

import ipyvuetify as v
import solara
from solara.alias import rv
from solara_enterprise import auth
import httpx
from solara.lab import Ref

from .components.clipboard import CopyToClipboard
from .state import GLOBAL_STATE, UserType
from .remote import BASE_API
from .components.hero import Hero
from .components.setup_dialog import UserTypeSetup

IMG_PATH = Path("static") / "public" / "images"


@solara.component
def Layout(children=[]):
    router = solara.use_router()
    route_current, routes = solara.use_route()
    show_menu = solara.use_reactive(False)

    def _check_user_status():
        if BASE_API.student_exists:
            Ref(GLOBAL_STATE.fields.user.user_type).set(UserType.student)
        elif BASE_API.educator_exists:
            Ref(GLOBAL_STATE.fields.user.user_type).set(UserType.educator)

    solara.use_effect(_check_user_status, [])

    with rv.App(dark=True) as main:
        solara.Title("Cosmic Data Stories")

        with rv.AppBar(elevate_on_scroll=True, app=True):

            with rv.Container(class_="py-0 fill-height"):
                with solara.Link(solara.resolve_path("/")):
                    with rv.Avatar(class_="mr-8", width="60", tile=True):
                        rv.Img(
                            src=str(IMG_PATH / "logo.webp"),
                        )

                solara.Button(
                    "Data Stories",
                    text=True,
                    on_click=lambda: router.push("/data_stories"),
                )
                solara.Button(
                    "Mini Stories", text=True, on_click=lambda: router.push("/")
                )

                rv.Spacer()

                if not Ref(GLOBAL_STATE.fields.user.is_validated).value:
                    solara.Button(
                        "Sign in", href=auth.get_login_url(), text=True, outlined=True
                    )
                else:
                    if not (BASE_API.student_exists or BASE_API.educator_exists):
                        UserTypeSetup()

                    solara.lab.ThemeToggle()
                    rv.Btn(icon=True, children=[rv.Icon(children=["mdi-bell"])])

                    with rv.Menu(
                        botton=True,
                        left=True,
                        offset_y=True,
                        offset_x=False,
                        v_model=show_menu.value,
                        on_v_model=show_menu.set,
                        v_slots=[
                            {
                                "name": "activator",
                                "variable": "x",
                                "children": rv.Btn(
                                    icon=True,
                                    class_="ml-2",
                                    children=[
                                        rv.Avatar(
                                            children=(
                                                [
                                                    rv.Img(
                                                        src=f"{auth.user.value['userinfo'].get('picture', '')}"
                                                    )
                                                ]
                                                if auth.user.value["userinfo"].get(
                                                    "picture"
                                                )
                                                is not None
                                                else [
                                                    rv.Icon(
                                                        children=["mdi-account-circle"]
                                                    )
                                                ]
                                            ),
                                        )
                                    ],
                                    text=True,
                                    outlined=True,
                                    v_on="x.on",
                                ),
                            }
                        ],
                    ):
                        with rv.List(dense=True, nav=True, max_width=300):
                            with rv.ListItem():
                                rv.ListItemAvatar(
                                    children=[
                                        rv.Img(
                                            src=f"{auth.user.value['userinfo'].get('picture', '')}"
                                        )
                                    ]
                                ),
                                rv.ListItemContent(
                                    children=[
                                        rv.ListItemTitle(
                                            children=[
                                                f"{auth.user.value['userinfo'].get('name', 'email')}",
                                                CopyToClipboard(
                                                    student_username=BASE_API.hashed_user
                                                ),
                                            ]
                                        ),
                                        rv.ListItemSubtitle(
                                            children=[
                                                f"{auth.user.value['userinfo'].get('email', '')}"
                                            ]
                                        ),
                                    ]
                                )

                            rv.Divider(class_="pb-1")

                            if (
                                Ref(GLOBAL_STATE.fields.user.user_type).value
                                == UserType.student
                            ):
                                with rv.ListItem(link=True) as classes_item:
                                    with rv.ListItemIcon():
                                        rv.Icon(children=["mdi-account"])

                                    rv.ListItemTitle(children=["My Classes"])

                                solara.v.use_event(
                                    classes_item,
                                    "click",
                                    lambda *args: router.push("/student_classes"),
                                )
                            elif (
                                Ref(GLOBAL_STATE.fields.user.user_type).value
                                == UserType.educator
                            ):
                                with rv.ListItem(link=True) as classes_item:
                                    with rv.ListItemIcon():
                                        rv.Icon(children=["mdi-chart-bubble"])

                                    rv.ListItemTitle(children=["Educator Dashboard"])

                                solara.v.use_event(
                                    classes_item,
                                    "click",
                                    lambda *args: router.push("/educator-dashboard"),
                                )
                                with rv.ListItem(link=True) as classes_item:
                                    with rv.ListItemIcon():
                                        rv.Icon(children=["mdi-book"])

                                    rv.ListItemTitle(children=["Manage Classes"])

                                solara.v.use_event(
                                    classes_item,
                                    "click",
                                    lambda *args: router.push("/manage_classes"),
                                )
                                with rv.ListItem(link=True) as classes_item:
                                    with rv.ListItemIcon():
                                        rv.Icon(children=["mdi-account-group"])

                                    rv.ListItemTitle(children=["Manage Students"])

                                solara.v.use_event(
                                    classes_item,
                                    "click",
                                    lambda *args: router.push("/manage_students"),
                                )

                            with rv.ListItem(link=True):
                                with rv.ListItemIcon():
                                    rv.Icon(children=["mdi-settings"])

                                rv.ListItemTitle(children=["Settings"])

                            rv.Divider(class_="pb-1")

                            solara.Button(
                                "Logout",
                                style="width:100%",
                                icon_name="mdi-logout",
                                color="error",
                                flat=True,
                                text=False,
                                on_click=lambda: router.push("/"),
                                href=auth.get_logout_url("/"),
                            )

        with rv.Content():
            if route_current.path == "/":
                Hero()

            with rv.Container(
                children=children,
                # class_="fill-height",
                style_="max-width: 1200px",
            ):
                pass

        with rv.Footer(
            app=False,
            padless=True,
            # style_="background: none !important;",
        ):
            with rv.Container(style="background: none; max-width: 1200px"):

                with rv.Row(class_="d-flex justify-center"):
                    with rv.Col(class_="d-flex justify-center"):
                        rv.Btn(children=["About"], text=True)
                        rv.Btn(children=["Team"], text=True)
                        rv.Btn(children=["Contact"], text=True)
                        rv.Btn(children=["Privacy"], text=True)
                        rv.Btn(children=["Digital Accessibility"], text=True)
                rv.Divider()

                with rv.Row():
                    with rv.Col(cols=4):
                        solara.Text("Cosmic Data Stories", classes=["title"])
                        solara.HTML(
                            unsafe_innerHTML="""
                                Center for Astrophysics Harvard | Smithsonian<br/>
                                60 Garden Street<br/>
                                Cambridge, MA  02138
                            """,
                            classes=["text-h6"],
                        )

                    with rv.Col(cols=4):
                        rv.Img(
                            src=str(IMG_PATH / "NASA_logo_svg.webp"),
                            contain=True,
                            height="100",
                        )

                    with rv.Col(cols=4):
                        rv.Img(
                            src=str(IMG_PATH / "cfa_theme_logo_black.webp"),
                            contain=True,
                            height=50,
                        )

                with rv.Row():
                    with rv.Col(class_="text-center", cols=10, offset=1):
                        solara.Div(
                            children=[
                                "The material contained on this website is based upon work supported by NASA under "
                                "award No. 80NSSC21M0002 Any opinions, findings, and conclusions or recommendations "
                                "expressed in this material are those of the author(s) and do not necessarily reflect "
                                "the views of the National Aeronautics and Space Administration."
                            ],
                            classes=["caption mb-4"],
                        )
                        solara.Text(
                            "Copyright © 2024 The President and Fellows of Harvard College",
                        )

    return main
