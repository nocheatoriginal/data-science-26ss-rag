from __future__ import annotations

import unittest

from bs4 import BeautifulSoup

from minecraft_wiki_scraper.crafting import parse_crafting_page_html, parse_recipe_cell


class CraftingParserTests(unittest.TestCase):
    def test_parse_category_recipe_table(self) -> None:
        html = """
        <html>
          <body>
            <h1 id="firstHeading">Crafting/Building blocks</h1>
            <table class="wikitable collapsible sortable">
              <tr>
                <th>Name</th>
                <th>Ingredients</th>
                <th>Crafting recipe</th>
                <th>Description</th>
              </tr>
              <tr>
                <th><a href="/w/Bricks" title="Bricks">Bricks</a></th>
                <td><a href="/w/Brick" title="Brick">Brick</a></td>
                <td style="padding:1px;text-align:center">
                  <div>
                    <span class="mcui mcui-Crafting_Table pixel-image">
                      <span class="mcui-input">
                        <span class="mcui-row">
                          <span class="invslot"></span>
                          <span class="invslot"></span>
                          <span class="invslot"></span>
                        </span>
                        <span class="mcui-row">
                          <span class="invslot">
                            <span class="invslot-item invslot-item-image">
                              <a href="/w/Brick" title="Brick"><img alt="Brick" /></a>
                            </span>
                          </span>
                          <span class="invslot">
                            <span class="invslot-item invslot-item-image">
                              <a href="/w/Brick" title="Brick"><img alt="Brick" /></a>
                            </span>
                          </span>
                          <span class="invslot"></span>
                        </span>
                        <span class="mcui-row">
                          <span class="invslot">
                            <span class="invslot-item invslot-item-image">
                              <a href="/w/Brick" title="Brick"><img alt="Brick" /></a>
                            </span>
                          </span>
                          <span class="invslot">
                            <span class="invslot-item invslot-item-image">
                              <a href="/w/Brick" title="Brick"><img alt="Brick" /></a>
                            </span>
                          </span>
                          <span class="invslot"></span>
                        </span>
                      </span>
                      <span class="mcui-output">
                        <span class="invslot invslot-large">
                          <span class="invslot-item invslot-item-image">
                            <a href="/w/Bricks" title="Bricks"><img alt="Bricks" /></a>
                          </span>
                          <a href="/w/Bricks" title="Bricks"><span class="invslot-stacksize">4</span></a>
                        </span>
                      </span>
                    </span>
                  </div>
                </td>
                <td></td>
              </tr>
            </table>
          </body>
        </html>
        """

        records = parse_crafting_page_html(html, "https://minecraft.wiki/w/Crafting/Building_blocks")
        self.assertEqual(len(records), 1)

        recipe = records[0]
        self.assertEqual(recipe["name"], "Bricks")
        self.assertEqual(recipe["source_page"], "Crafting/Building_blocks")
        self.assertEqual(recipe["station"], "Crafting Table")
        self.assertFalse(recipe["shapeless"])
        self.assertEqual(recipe["output_items"], ["Bricks"])
        self.assertEqual(recipe["output_count"], 4)
        self.assertEqual(recipe["grid"][1][0], ["Brick"])
        self.assertIsNone(recipe["grid"][0][0])

    def test_parse_item_page_without_name_column(self) -> None:
        html = """
        <html>
          <body>
            <h1 id="firstHeading">Diamond Sword</h1>
            <table class="wikitable collapsible" data-description="Crafting recipes">
              <tr>
                <th>Ingredients</th>
                <th>Crafting recipe</th>
              </tr>
              <tr>
                <td><a href="/w/Diamond" title="Diamond">Diamond</a> + <a href="/w/Stick" title="Stick">Stick</a></td>
                <td>
                  <span class="mcui mcui-Crafting_Table pixel-image">
                    <span class="mcui-input">
                      <span class="mcui-row">
                        <span class="invslot"></span>
                        <span class="invslot">
                          <span class="invslot-item invslot-item-image">
                            <a href="/w/Diamond" title="Diamond"><img alt="Diamond" /></a>
                          </span>
                        </span>
                        <span class="invslot"></span>
                      </span>
                      <span class="mcui-row">
                        <span class="invslot"></span>
                        <span class="invslot">
                          <span class="invslot-item invslot-item-image">
                            <a href="/w/Diamond" title="Diamond"><img alt="Diamond" /></a>
                          </span>
                        </span>
                        <span class="invslot"></span>
                      </span>
                      <span class="mcui-row">
                        <span class="invslot"></span>
                        <span class="invslot">
                          <span class="invslot-item invslot-item-image">
                            <a href="/w/Stick" title="Stick"><img alt="Stick" /></a>
                          </span>
                        </span>
                        <span class="invslot"></span>
                      </span>
                    </span>
                    <span class="mcui-output">
                      <span class="invslot invslot-large">
                        <span class="invslot-item invslot-item-image">
                          <span title="Diamond Sword"><img alt="Diamond Sword" /></span>
                        </span>
                      </span>
                    </span>
                  </span>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """

        records = parse_crafting_page_html(html, "https://minecraft.wiki/w/Diamond_Sword")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Diamond Sword")
        self.assertEqual(records[0]["ingredient_links"], ["Diamond", "Stick"])
        self.assertEqual(records[0]["output_items"], ["Diamond Sword"])

    def test_parse_shapeless_recipe_with_variants(self) -> None:
        html = """
        <td>
          <span class="mcui mcui-Crafting_Table pixel-image">
            <span class="mcui-input">
              <span class="mcui-row">
                <span class="invslot"></span>
                <span class="invslot"></span>
                <span class="invslot"></span>
              </span>
              <span class="mcui-row">
                <span class="invslot animated">
                  <span class="invslot-item invslot-item-image">
                    <a href="/w/Bundle" title="Bundle"><img alt="Bundle" /></a>
                  </span>
                  <span class="invslot-item invslot-item-image">
                    <a href="/w/White_Bundle" title="White Bundle"><img alt="White Bundle" /></a>
                  </span>
                </span>
                <span class="invslot">
                  <span class="invslot-item invslot-item-image">
                    <a href="/w/Blue_Dye" title="Blue Dye"><img alt="Blue Dye" /></a>
                  </span>
                </span>
                <span class="invslot"></span>
              </span>
            </span>
            <span class="mcui-output">
              <span class="invslot invslot-large">
                <span class="invslot-item invslot-item-image">
                  <a href="/w/Blue_Bundle" title="Blue Bundle"><img alt="Blue Bundle" /></a>
                </span>
              </span>
            </span>
            <span class="mcui-icons">
              <span class="mcui-shapeless" title="This recipe is shapeless."><br /></span>
            </span>
          </span>
        </td>
        """

        cell = BeautifulSoup(html, "html.parser").td
        assert cell is not None
        recipe = parse_recipe_cell(cell)

        self.assertTrue(recipe["shapeless"])
        self.assertEqual(recipe["grid"][1][0], ["Bundle", "White Bundle"])
        self.assertEqual(recipe["output_items"], ["Blue Bundle"])


if __name__ == "__main__":
    unittest.main()
