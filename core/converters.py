class ObjectIdConverter:
  # 24-znakowy hex (Mongo ObjectId)
  regex = r"[0-9a-f]{24}"

  def to_python(self, value: str) -> str:
    return value

  def to_url(self, value: str) -> str:
    return str(value)
