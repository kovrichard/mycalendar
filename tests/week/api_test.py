from tests import AppTestCase, TestClientMixin, TemplateRenderMixin
from truth.truth import AssertThat

class WeekTest(TestClientMixin, TemplateRenderMixin, AppTestCase):
    def test_get_week_renders_week_template(self):
        week_num = 2
        r = self.client.get("/week/" + str(week_num))
        template, context = self.rendered_templates[0]
        
        AssertThat(r.status_code).IsEqualTo(200)
        AssertThat(template.name).IsEqualTo("week.html")
        AssertThat(context["week_number"]).IsEqualTo(week_num)
