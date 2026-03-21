ALTER TABLE `tabAsset Category` DROP COLUMN IF EXISTS `parent_category`;
ALTER TABLE `tabAsset Category` DROP COLUMN IF EXISTS `is_group`;
SELECT 'columns dropped';
