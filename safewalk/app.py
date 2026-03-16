"""SafeWalk - Huvudapplikation."""

import json
import os

import gi
from safewalk.i18n import _
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ROUTES_FILE = os.path.join(DATA_DIR, "routes.json")


def load_data():
    with open(ROUTES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ROUTES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class SafeWalkWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("SafeWalk")
        self.set_default_size(400, 700)

        self.data = load_data()
        self.walking = False
        self.current_route = None
        self.current_step = 0
        self.sim_timer_id = None

        # Huvudlayout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        # Header bar
        header = Adw.HeaderBar()
        self.main_box.append(header)

        # Stack för olika vyer
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.main_box.append(self.stack)

        self._build_home_page()
        self._build_walking_page()
        self._build_contacts_page()

        # Bottom navigation
        nav_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        nav_bar.set_homogeneous(True)
        nav_bar.add_css_class("toolbar")
        self.main_box.append(nav_bar)

        for label, page_name in [("Hem", "home"), ("Kontakter", "contacts")]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", self._on_nav, page_name)
            nav_bar.append(btn)

    # ── Hemvyn ──────────────────────────────────────────

    def _build_home_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.set_margin_top(20)
        page.set_margin_bottom(20)
        page.set_margin_start(20)
        page.set_margin_end(20)
        page.set_vexpand(True)

        # Titel
        title = Gtk.Label(label=_("SafeWalk")
        title.add_css_class("title-1")
        page.append(title)

        subtitle = Gtk.Label(label=_("Kom hem tryggt")
        subtitle.add_css_class("dim-label")
        page.append(subtitle)

        # Status
        self.status_label = Gtk.Label(label=_("Select a route to start")
        self.status_label.set_wrap(True)
        self.status_label.set_margin_top(10)
        page.append(self.status_label)

        # Ruttlista
        route_frame = Gtk.Frame(label=_("Sparade rutter")
        route_frame.set_margin_top(10)
        page.append(route_frame)

        route_list = Gtk.ListBox()
        route_list.set_selection_mode(Gtk.SelectionMode.NONE)
        route_list.add_css_class("boxed-list")
        route_frame.set_child(route_list)

        for i, route in enumerate(self.data["routes"]):
            row = Adw.ActionRow()
            row.set_title(route["name"])
            row.set_subtitle(f"Ca {route['estimated_minutes']} min · {len(route['steps'])} stopp")

            btn = Gtk.Button(label=_("Start")
            btn.add_css_class("suggested-action")
            btn.set_valign(Gtk.Align.CENTER)
            btn.connect("clicked", self._on_start_walk, i)
            row.add_suffix(btn)

            route_list.append(row)

        self.stack.add_named(page, "home")

    # ── Promenadvyn ─────────────────────────────────────

    def _build_walking_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        page.set_margin_top(20)
        page.set_margin_bottom(20)
        page.set_margin_start(20)
        page.set_margin_end(20)
        page.set_vexpand(True)

        walk_title = Gtk.Label(label=_("Walk in progress")
        walk_title.add_css_class("title-2")
        page.append(walk_title)

        # Ruttnamn
        self.route_name_label = Gtk.Label(label=_("")
        self.route_name_label.add_css_class("title-3")
        page.append(self.route_name_label)

        # Progress
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        page.append(self.progress_bar)

        # Aktuell position
        pos_frame = Gtk.Frame(label=_("Position")
        page.append(pos_frame)

        pos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        pos_box.set_margin_top(10)
        pos_box.set_margin_bottom(10)
        pos_box.set_margin_start(10)
        pos_box.set_margin_end(10)
        pos_frame.set_child(pos_box)

        self.position_label = Gtk.Label(label=_("Simulerar position...")
        self.position_label.set_wrap(True)
        pos_box.append(self.position_label)

        self.coords_label = Gtk.Label(label=_("")
        self.coords_label.add_css_class("dim-label")
        self.coords_label.set_selectable(True)
        pos_box.append(self.coords_label)

        # Steg-lista
        self.steps_list = Gtk.ListBox()
        self.steps_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.steps_list.add_css_class("boxed-list")

        steps_scroll = Gtk.ScrolledWindow()
        steps_scroll.set_vexpand(True)
        steps_scroll.set_child(self.steps_list)
        page.append(steps_scroll)

        # Knappar
        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        page.append(btn_box)

        # Dela position
        share_btn = Gtk.Button(label=_("Dela min position")
        share_btn.add_css_class("suggested-action")
        share_btn.connect("clicked", self._on_share_position)
        btn_box.append(share_btn)

        # Jag är framme
        self.arrived_btn = Gtk.Button(label=_("I have arrived!")
        self.arrived_btn.add_css_class("success")
        self.arrived_btn.connect("clicked", self._on_arrived)
        btn_box.append(self.arrived_btn)

        # SOS / Avbryt
        cancel_btn = Gtk.Button(label=_("Cancel promenad")
        cancel_btn.add_css_class("destructive-action")
        cancel_btn.connect("clicked", self._on_cancel_walk)
        btn_box.append(cancel_btn)

        self.stack.add_named(page, "walking")

    # ── Kontaktvyn ──────────────────────────────────────

    def _build_contacts_page(self):
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page.set_margin_top(20)
        page.set_margin_bottom(20)
        page.set_margin_start(20)
        page.set_margin_end(20)
        page.set_vexpand(True)

        title = Gtk.Label(label=_("Trygga kontakter")
        title.add_css_class("title-2")
        page.append(title)

        desc = Gtk.Label(label=_("Dessa personer kan se din position under promenader.")
        desc.set_wrap(True)
        desc.add_css_class("dim-label")
        page.append(desc)

        self.contacts_list = Gtk.ListBox()
        self.contacts_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.contacts_list.add_css_class("boxed-list")
        page.append(self.contacts_list)

        self._refresh_contacts()

        # Lägg till kontakt
        add_frame = Gtk.Frame(label=_("Add kontakt")
        add_frame.set_margin_top(10)
        page.append(add_frame)

        add_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        add_box.set_margin_top(10)
        add_box.set_margin_bottom(10)
        add_box.set_margin_start(10)
        add_box.set_margin_end(10)
        add_frame.set_child(add_box)

        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text(_("Name")
        add_box.append(self.name_entry)

        self.phone_entry = Gtk.Entry()
        self.phone_entry.set_placeholder_text(_("Telefonnummer")
        add_box.append(self.phone_entry)

        add_btn = Gtk.Button(label=_("Add")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", self._on_add_contact)
        add_box.append(add_btn)

        self.stack.add_named(page, "contacts")

    def _refresh_contacts(self):
        while True:
            child = self.contacts_list.get_first_child()
            if child is None:
                break
            self.contacts_list.remove(child)

        for contact in self.data["contacts"]:
            row = Adw.ActionRow()
            row.set_title(contact["name"])
            row.set_subtitle(contact["phone"])
            row.add_prefix(Gtk.Image.new_from_icon_name("contact-new-symbolic"))
            self.contacts_list.append(row)

    # ── Callbacks ───────────────────────────────────────

    def _on_nav(self, button, page_name):
        if self.walking and page_name == "home":
            page_name = "walking"
        self.stack.set_visible_child_name(page_name)

    def _on_start_walk(self, button, route_index):
        self.current_route = self.data["routes"][route_index]
        self.current_step = 0
        self.walking = True

        self.route_name_label.set_label(self.current_route["name"])
        self._update_walk_display()
        self._populate_steps_list()

        # Meddela kontakter
        contacts = ", ".join(c["name"] for c in self.data["contacts"])
        self._show_toast(f"Position delas med: {contacts}")

        self.stack.set_visible_child_name("walking")

        # Starta GPS-simulering
        self.sim_timer_id = GLib.timeout_add_seconds(4, self._sim_advance)

    def _populate_steps_list(self):
        while True:
            child = self.steps_list.get_first_child()
            if child is None:
                break
            self.steps_list.remove(child)

        for i, step in enumerate(self.current_route["steps"]):
            row = Adw.ActionRow()
            row.set_title(step["name"])
            row.set_subtitle(f"{step['lat']:.4f}, {step['lon']:.4f}")
            if i < self.current_step:
                row.add_prefix(Gtk.Image.new_from_icon_name("emblem-ok-symbolic"))
            elif i == self.current_step:
                row.add_prefix(Gtk.Image.new_from_icon_name("find-location-symbolic"))
            else:
                row.add_prefix(Gtk.Image.new_from_icon_name("radio-symbolic"))
            self.steps_list.append(row)

    def _update_walk_display(self):
        if not self.current_route:
            return
        steps = self.current_route["steps"]
        step = steps[self.current_step]
        total = len(steps)

        self.position_label.set_label(f"Du är vid: {step['name']}")
        self.coords_label.set_label(f"({step['lat']:.4f}, {step['lon']:.4f})")

        fraction = self.current_step / max(total - 1, 1)
        self.progress_bar.set_fraction(fraction)
        self.progress_bar.set_text(f"Steg {self.current_step + 1} av {total}")

    def _sim_advance(self):
        if not self.walking or not self.current_route:
            return False

        steps = self.current_route["steps"]
        if self.current_step < len(steps) - 1:
            self.current_step += 1
            self._update_walk_display()
            self._populate_steps_list()

            if self.current_step == len(steps) - 1:
                self._show_toast("Du verkar ha kommit fram! Tryck 'Jag är framme!'")
                return False
            return True
        return False

    def _on_share_position(self, button):
        if not self.current_route:
            self._show_toast("Ingen aktiv promenad.")
            return

        step = self.current_route["steps"][self.current_step]
        msg = (
            f"SafeWalk: Jag går '{self.current_route['name']}'. "
            f"Just nu vid {step['name']} "
            f"({step['lat']:.4f}, {step['lon']:.4f})"
        )

        # Kopiera till clipboard
        clipboard = self.get_clipboard()
        clipboard.set(msg)

        contacts = ", ".join(c["name"] for c in self.data["contacts"])
        self._show_toast(f"Position kopierad! Skicka till: {contacts}")

    def _on_arrived(self, button):
        if not self.walking:
            self._show_toast("Ingen aktiv promenad.")
            return

        self.walking = False
        if self.sim_timer_id:
            GLib.source_remove(self.sim_timer_id)
            self.sim_timer_id = None

        route_name = self.current_route["name"]
        contacts = ", ".join(c["name"] for c in self.data["contacts"])

        dialog = Adw.AlertDialog()
        dialog.set_heading("Framme!")
        dialog.set_body(
            f"Du har bekräftat att du är framme.\n"
            f"Rutt: {route_name}\n\n"
            f"Meddelande skickas till: {contacts}\n"
            f"\"Jag är framme och trygg!\""
        )
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.choose(self, None, None)

        self.current_route = None
        self.current_step = 0
        self.stack.set_visible_child_name("home")
        self.status_label.set_label("Senaste promenad avslutad. Välj en ny rutt!")

    def _on_cancel_walk(self, button):
        self.walking = False
        if self.sim_timer_id:
            GLib.source_remove(self.sim_timer_id)
            self.sim_timer_id = None
        self.current_route = None
        self.current_step = 0
        self.stack.set_visible_child_name("home")
        self.status_label.set_label("Promenad avbruten. Välj en ny rutt!")

    def _on_add_contact(self, button):
        name = self.name_entry.get_text().strip()
        phone = self.phone_entry.get_text().strip()
        if not name or not phone:
            self._show_toast("Fyll i både namn och telefonnummer.")
            return

        self.data["contacts"].append({"name": name, "phone": phone})
        save_data(self.data)
        self._refresh_contacts()
        self.name_entry.set_text("")
        self.phone_entry.set_text("")
        self._show_toast(f"{name} tillagd som trygg kontakt!")

    def _show_toast(self, message):
        toast = Adw.Toast(title=message)
        toast.set_timeout(3)
        # Find or create toast overlay
        if not hasattr(self, "_toast_overlay"):
            self._toast_overlay = Adw.ToastOverlay()
            content = self.main_box
            self.set_content(self._toast_overlay)
            self._toast_overlay.set_child(content)
        self._toast_overlay.add_toast(toast)


class SafeWalkApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="se.safewalk.app")

    def do_activate(self):
        win = SafeWalkWindow(application=self)
        win.present()


def main():
    app = SafeWalkApp()
    app.run()


if __name__ == "__main__":
    main()
