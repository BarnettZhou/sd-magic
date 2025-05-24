export interface CategoryData {
  id: number
  name: string,
  parentId: number,
  isDefault: boolean,
  children: CategoryData[]
}