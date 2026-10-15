from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("users", "0002_customuser_auth_flags")]

    # Match the current model, where the old role field was commented out.
    # Applying this migration removes any existing values in that column.
    operations = [migrations.RemoveField(model_name="customuser", name="role")]
