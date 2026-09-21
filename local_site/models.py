from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    is_head_office = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Contact
    address = models.TextField()
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    # Location
    google_map_url = models.URLField(blank=True)
    google_map_embed = models.TextField(blank=True)

    # Landing Page
    hero_title = models.CharField(max_length=200, blank=True)
    hero_subtitle = models.TextField(blank=True)
    offer_text = models.CharField(max_length=200, blank=True)

    # SEO
    seo_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    # Google Business Profile
    google_review_url = models.URLField(blank=True)

    # Marketing
    monthly_marketing_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
class LocalTestimonial(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="testimonials"
    )

    student_name = models.CharField(max_length=120)
    course_name = models.CharField(max_length=150, blank=True)

    photo = models.ImageField(
        upload_to="local_site/testimonials/",
        blank=True,
        null=True
    )

    review = models.TextField()

    rating = models.PositiveSmallIntegerField(default=5)

    is_google_review = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return f"{self.student_name} - {self.branch.name}"


class BranchGallery(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )

    title = models.CharField(max_length=150, blank=True)

    image = models.ImageField(
        upload_to="local_site/gallery/"
    )

    alt_text = models.CharField(
        max_length=200,
        blank=True
    )

    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return f"{self.branch.name} - {self.title or 'Gallery'}"
