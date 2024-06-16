from django_components.component import register, Component


@register("modal-form")
class ModalForm(Component):
    template_name = "modal_form/team_create_modal_form.html"

    class Media:
        js = [
            "observe-node-insertion.js",
            "modal_form/team_create_modal_form.js",
        ]
