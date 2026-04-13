    def _parse_response(self, content: str, platform: str, language: str) -> CopywritingResult:
        """解析 API 返回的文本"""

        lines = content.strip().split('\n')

        title = ""
        description = ""
        bullet_points = []
        hashtags = []
        seo_keywords = []

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 识别各个部分
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                current_section = "title"
            elif line.startswith("DESCRIPTION:"):
                # DESCRIPTION: 可能在同一行，也可能在下一行
                desc_content = line.replace("DESCRIPTION:", "").strip()
                if desc_content:
                    description = desc_content
                current_section = "description"
            elif line.startswith("BULLET_POINTS:"):
                current_section = "bullet"
            elif line.startswith("HASHTAGS:"):
                current_section = "hashtags"
            elif line.startswith("SEO_KEYWORDS:"):
                seo_keywords = [k.strip() for k in line.replace("SEO_KEYWORDS:", "").split(",") if k.strip()]
                current_section = "seo"
            elif current_section == "description":
                # 描述内容（多行）
                if description:
                    description += " " + line
                else:
                    description = line
            elif line.startswith("- ") and current_section == "bullet":
                bullet_points.append(line[2:].strip())
            elif line.startswith("#") and current_section == "hashtags":
                # 提取 hashtags
                tags = [t.strip() for t in line.split() if t.startswith("#")]
                hashtags.extend(tags)

        return CopywritingResult(
            title=title,
            description=description.strip(),
            bullet_points=bullet_points,
            hashtags=hashtags,
            seo_keywords=seo_keywords,
            platform=platform,
            language=language
        )
