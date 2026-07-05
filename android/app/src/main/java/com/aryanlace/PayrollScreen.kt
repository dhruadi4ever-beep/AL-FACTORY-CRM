package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class PayrollRow(
    val employee: String,
    val hours: String,
    val status: String,
    val advance: String,
)

@Composable
fun PayrollScreen() {
    val rows = remember {
        listOf(
            PayrollRow("Ravi", "48.5", "Finalized", "₹1500"),
            PayrollRow("Kiran", "40.0", "Draft", "₹500"),
        )
    }

    var employee by remember { mutableStateOf("Ravi") }
    var hours by remember { mutableStateOf("8.0") }
    var advance by remember { mutableStateOf("500") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Employee Attendance & Salary", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Weekly hour-based payroll with manual advance deductions")

        Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
            Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = employee, onValueChange = { employee = it }, label = { Text("Employee") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = hours, onValueChange = { hours = it }, label = { Text("Working Hours") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(value = advance, onValueChange = { advance = it }, label = { Text("Advance") }, modifier = Modifier.fillMaxWidth())
            }
        }

        Text(text = "Weekly Overview", style = MaterialTheme.typography.titleMedium)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(rows) { row ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            Text(text = row.employee, style = MaterialTheme.typography.titleSmall)
                            Text(text = "Hours: ${row.hours}")
                        }
                        Column(horizontalAlignment = Alignment.End, verticalArrangement = Arrangement.spacedBy(2.dp)) {
                            Text(text = row.status)
                            Text(text = "Advance: ${row.advance}")
                        }
                    }
                }
            }
        }
    }
}
