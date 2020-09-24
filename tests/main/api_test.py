from tests import AppTestCase, TemplateRenderMixin, TestClientMixin

from truth.truth import AssertThat

class TestApi(TestClientMixin, TemplateRenderMixin, AppTestCase):
    def test_welcome_renders_template(self):
        r = self.client.get("/")
        template, context = self.rendered_templates[0]
        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("welcome.html")